"""
Feature engineering module for ASLPS.

Implements all feature extraction logic:
- Usage frequency (time-decayed)
- Category similarity for cold-start
- Shelf proximity (graph distance)
- Pathway congestion score
- Availability constraints (space)
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

from api.models import Component, Shelf, MovementLog

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Feature engineering class for extracting ML features.
    
    Handles all 5 edge cases:
    1. Sudden demand spike
    2. Limited availability of optimal shelf
    3. Restricted/Hazard-area components
    4. New components with no history
    5. Congestion avoidance in high-traffic paths
    """
    
    def __init__(self):
        """Initialize feature engineer."""
        self.decay_factor = 0.95  # Time decay factor for usage frequency
        self.congestion_window_hours = 2  # Time window for congestion calculation
    
    def extract_features(
        self,
        component: Component,
        shelf: Shelf,
        all_shelves: List[Shelf],
        movement_logs: List[MovementLog]
    ) -> Dict[str, float]:
        """
        Extract comprehensive feature vector for component-shelf pair.
        
        Args:
            component: Component instance
            shelf: Shelf instance
            all_shelves: List of all shelves (for proximity calculation)
            movement_logs: List of recent movement logs
            
        Returns:
            Dictionary of feature names and values
        """
        features = {}
        
        # 1. Usage frequency (time-decayed)
        features['usage_frequency'] = self._calculate_usage_frequency(
            component, movement_logs
        )
        
        # 2. Category similarity (for cold-start)
        features['category_similarity'] = self._calculate_category_similarity(
            component, shelf, all_shelves
        )
        
        # 3. Shelf proximity (graph distance)
        features['shelf_proximity'] = self._calculate_shelf_proximity(
            shelf, all_shelves
        )
        
        # 4. Pathway congestion score
        features['pathway_congestion'] = self._calculate_pathway_congestion(
            shelf, movement_logs
        )
        
        # 5. Availability constraints (space)
        features['space_availability'] = self._calculate_space_availability(
            component, shelf
        )
        
        # Additional features
        features['distance_to_entrance'] = shelf.distance_to_entrance
        features['shelf_congestion_score'] = shelf.current_congestion_score
        features['is_hazardous_match'] = 1.0 if (
            component.is_hazardous == shelf.is_hazardous_zone
        ) else 0.0
        features['climate_control_match'] = 1.0 if (
            component.requires_climate_control == shelf.has_climate_control
        ) else 0.0
        
        # Weight and volume ratios
        weight_ratio = (shelf.current_weight_kg + component.weight_kg) / shelf.max_weight_kg
        volume_ratio = (shelf.current_volume_m3 + 
                       component.length_m * component.width_m * component.height_m) / shelf.max_volume_m3
        features['weight_utilization'] = weight_ratio
        features['volume_utilization'] = volume_ratio
        
        # Zone preference (if component has history)
        features['zone_preference'] = self._calculate_zone_preference(
            component, shelf, movement_logs
        )
        
        return features
    
    def _calculate_usage_frequency(
        self,
        component: Component,
        movement_logs: List[MovementLog]
    ) -> float:
        """
        Calculate time-decayed usage frequency.
        
        Handles edge case: Sudden demand spike (recent movements weighted higher)
        """
        if not movement_logs:
            # Edge case 4: New component with no history
            return 0.0
        
        now = datetime.utcnow()
        total_score = 0.0
        
        for log in movement_logs:
            if log.component_id != component.component_id:
                continue
            if log.movement_type != 'RETRIEVAL':
                continue
            
            # Time decay: more recent = higher weight
            hours_ago = (now - log.timestamp).total_seconds() / 3600
            decay_weight = self.decay_factor ** hours_ago
            total_score += decay_weight
        
        # Normalize by component's total retrievals
        if component.total_retrievals > 0:
            return total_score / component.total_retrievals
        
        return total_score
    
    def _calculate_category_similarity(
        self,
        component: Component,
        shelf: Shelf,
        all_shelves: List[Shelf]
    ) -> float:
        """
        Calculate category similarity for cold-start handling.
        
        Edge case 4: New components use category-based similarity
        """
        # Find components in same category stored in this shelf
        similar_components = Component.objects.filter(category=component.category)
        
        if not similar_components:
            # No similar components, return neutral score
            return 0.5
        
        # Count how many similar components are in this shelf
        shelf_components = 0
        for comp in similar_components:
            # Check if component is stored in this shelf (via movement logs)
            recent_logs = MovementLog.objects.filter(
                component_id=comp.component_id,
                shelf_id=shelf.shelf_id,
                movement_type='STORAGE'
            ).order_by('-timestamp')
            
            if recent_logs:
                # Check if not retrieved (still stored)
                latest_storage = recent_logs.first()
                retrieval_after = MovementLog.objects.filter(
                    component_id=comp.component_id,
                    movement_type='RETRIEVAL',
                    timestamp__gt=latest_storage.timestamp
                ).first()
                
                if not retrieval_after:
                    shelf_components += 1
        
        # Normalize by total similar components
        total_similar = len(similar_components)
        return shelf_components / max(total_similar, 1)
    
    def _calculate_shelf_proximity(
        self,
        shelf: Shelf,
        all_shelves: List[Shelf]
    ) -> float:
        """
        Calculate shelf proximity using graph distance.
        
        Uses BFS to find shortest path to entrance.
        """
        if not shelf.adjacent_shelves:
            # Isolated shelf, return high distance
            return 100.0
        
        # Use distance_to_entrance if available
        if shelf.distance_to_entrance > 0:
            return shelf.distance_to_entrance
        
        # Otherwise, calculate using graph traversal
        visited = set()
        queue = [(shelf.shelf_id, 0)]
        shelf_dict = {s.shelf_id: s for s in all_shelves}
        
        while queue:
            current_id, distance = queue.pop(0)
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            if current_id not in shelf_dict:
                continue
            
            current_shelf = shelf_dict[current_id]
            
            # Check if this is an entrance shelf (distance_to_entrance = 0)
            if current_shelf.distance_to_entrance == 0:
                return distance
            
            # Add adjacent shelves to queue
            for adj_id in current_shelf.adjacent_shelves:
                if adj_id not in visited:
                    queue.append((adj_id, distance + 1))
        
        # If no path found, return high distance
        return 100.0
    
    def _calculate_pathway_congestion(
        self,
        shelf: Shelf,
        movement_logs: List[MovementLog]
    ) -> float:
        """
        Calculate pathway congestion score.
        
        Edge case 5: Congestion avoidance in high-traffic paths
        """
        if not movement_logs:
            return 0.0
        
        now = datetime.utcnow()
        time_threshold = now - timedelta(hours=self.congestion_window_hours)
        
        # Count movements in this shelf and adjacent shelves
        shelf_movements = sum(
            1 for log in movement_logs
            if log.shelf_id == shelf.shelf_id and log.timestamp >= time_threshold
        )
        
        # Count movements in adjacent shelves (pathway congestion)
        adjacent_movements = 0
        for log in movement_logs:
            if log.shelf_id in shelf.adjacent_shelves and log.timestamp >= time_threshold:
                adjacent_movements += 1
        
        # Normalize congestion score (0-1)
        total_movements = shelf_movements + adjacent_movements
        congestion_score = min(total_movements / 20.0, 1.0)  # Cap at 1.0
        
        return congestion_score
    
    def _calculate_space_availability(
        self,
        component: Component,
        shelf: Shelf
    ) -> float:
        """
        Calculate space availability score.
        
        Edge case 2: Limited availability of optimal shelf
        """
        component_volume = component.length_m * component.width_m * component.height_m
        
        # Check if component fits
        if shelf.available_space_m3 < component_volume:
            return 0.0
        
        # Calculate availability ratio
        availability_ratio = shelf.available_space_m3 / shelf.max_volume_m3
        
        # Also consider weight
        weight_availability = (
            (shelf.max_weight_kg - shelf.current_weight_kg) / shelf.max_weight_kg
        )
        
        # Combined availability score
        return (availability_ratio + weight_availability) / 2.0
    
    def _calculate_zone_preference(
        self,
        component: Component,
        shelf: Shelf,
        movement_logs: List[MovementLog]
    ) -> float:
        """
        Calculate zone preference based on historical storage.
        """
        component_logs = [
            log for log in movement_logs
            if log.component_id == component.component_id
        ]
        
        if not component_logs:
            return 0.5  # Neutral preference
        
        # Count how many times component was stored in this zone
        zone_count = sum(
            1 for log in component_logs
            if log.shelf_id == shelf.shelf_id or
            any(s.shelf_id == log.shelf_id and s.location.zone == shelf.location.zone
                for s in [shelf])  # Simplified check
        )
        
        return min(zone_count / len(component_logs), 1.0)

