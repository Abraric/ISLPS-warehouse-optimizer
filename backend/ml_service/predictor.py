"""
ML prediction service using Random Forest model.

Handles model loading, feature extraction, and prediction with edge case handling.
"""
import pickle
import os
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from django.conf import settings

from api.models import Component, Shelf, MovementLog
from .feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class LocationPredictor:
    """
    Main prediction service for storage location recommendations.
    
    Handles all 5 edge cases:
    1. Sudden demand spike
    2. Limited availability of optimal shelf
    3. Restricted/Hazard-area components
    4. New components with no history
    5. Congestion avoidance in high-traffic paths
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize predictor with trained model.
        
        Args:
            model_path: Path to saved model file (defaults to settings)
        """
        self.model_path = model_path or settings.ML_MODEL_PATH
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.feature_names = [
            'usage_frequency',
            'category_similarity',
            'shelf_proximity',
            'pathway_congestion',
            'space_availability',
            'distance_to_entrance',
            'shelf_congestion_score',
            'is_hazardous_match',
            'climate_control_match',
            'weight_utilization',
            'volume_utilization',
            'zone_preference',
        ]
        self._load_model()
    
    def _load_model(self):
        """Load trained Random Forest model from disk."""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded ML model from {self.model_path}")
            else:
                logger.warning(f"Model file not found at {self.model_path}. Using fallback logic.")
                self.model = None
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model = None
    
    def predict(
        self,
        component_id: str,
        consider_congestion: bool = True,
        preferred_zones: Optional[List[str]] = None
    ) -> Dict:
        """
        Predict optimal storage location for a component.
        
        Args:
            component_id: ID of component to store
            consider_congestion: Whether to consider congestion in prediction
            preferred_zones: List of preferred zone IDs (optional)
        
        Returns:
            Dictionary with prediction results including:
            - recommended_shelf_id
            - confidence_score
            - alternative_shelves
            - reasoning
            - feature_vector
        """
        try:
            # Get component
            try:
                component = Component.objects.get(component_id=component_id)
            except Component.DoesNotExist:
                return {
                    'error': f'Component {component_id} not found',
                    'recommended_shelf_id': None,
                    'confidence_score': 0.0,
                }
            
            # Get all available shelves
            all_shelves = list(Shelf.objects.filter(is_available=True))
            
            if not all_shelves:
                return {
                    'error': 'No available shelves found',
                    'recommended_shelf_id': None,
                    'confidence_score': 0.0,
                }
            
            # Get recent movement logs for feature engineering
            from datetime import datetime, timedelta
            time_threshold = datetime.utcnow() - timedelta(hours=24)
            movement_logs = list(
                MovementLog.objects.filter(timestamp__gte=time_threshold)
            )
            
            # Filter shelves based on constraints (Edge case 3: Restricted/Hazard)
            candidate_shelves = self._filter_candidate_shelves(
                component, all_shelves, preferred_zones
            )
            
            if not candidate_shelves:
                return {
                    'error': 'No suitable shelves found matching component requirements',
                    'recommended_shelf_id': None,
                    'confidence_score': 0.0,
                }
            
            # Extract features and make predictions
            predictions = []
            for shelf in candidate_shelves:
                # Extract features
                features = self.feature_engineer.extract_features(
                    component, shelf, all_shelves, movement_logs
                )
                
                # Adjust for congestion if requested (Edge case 5)
                if consider_congestion:
                    # Penalize high congestion
                    features['pathway_congestion'] *= -1  # Negative weight
                
                # Convert to feature vector
                feature_vector = np.array([
                    features.get(name, 0.0) for name in self.feature_names
                ]).reshape(1, -1)
                
                # Get prediction score
                if self.model:
                    # Use ML model prediction
                    score = self.model.predict_proba(feature_vector)[0][1]  # Probability of being optimal
                else:
                    # Fallback: rule-based scoring
                    score = self._rule_based_score(features, component, shelf)
                
                predictions.append({
                    'shelf': shelf,
                    'score': float(score),
                    'features': features,
                    'feature_vector': feature_vector[0].tolist(),
                })
            
            # Sort by score (highest first)
            predictions.sort(key=lambda x: x['score'], reverse=True)
            
            # Edge case 2: Limited availability - check if top shelf is actually available
            top_prediction = predictions[0]
            recommended_shelf = top_prediction['shelf']
            
            # Verify shelf can still store component
            can_store, reason = recommended_shelf.can_store(component)
            if not can_store:
                # Try next best option
                for pred in predictions[1:]:
                    shelf = pred['shelf']
                    can_store, reason = shelf.can_store(component)
                    if can_store:
                        top_prediction = pred
                        recommended_shelf = shelf
                        break
                
                if not can_store:
                    return {
                        'error': 'Top recommended shelves are no longer available',
                        'recommended_shelf_id': None,
                        'confidence_score': 0.0,
                    }
            
            # Prepare response
            response = {
                'component_id': component_id,
                'recommended_shelf_id': recommended_shelf.shelf_id,
                'confidence_score': top_prediction['score'],
                'alternative_shelves': [
                    {
                        'shelf_id': pred['shelf'].shelf_id,
                        'score': pred['score'],
                        'zone': pred['shelf'].location.zone,
                    }
                    for pred in predictions[1:6]  # Top 5 alternatives
                ],
                'reasoning': self._generate_reasoning(
                    top_prediction, component, recommended_shelf
                ),
                'feature_vector': {
                    name: float(top_prediction['features'].get(name, 0.0))
                    for name in self.feature_names
                },
            }
            
            logger.info(
                f"Prediction for {component_id}: "
                f"shelf={recommended_shelf.shelf_id}, "
                f"confidence={top_prediction['score']:.3f}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'recommended_shelf_id': None,
                'confidence_score': 0.0,
            }
    
    def _filter_candidate_shelves(
        self,
        component: Component,
        all_shelves: List[Shelf],
        preferred_zones: Optional[List[str]]
    ) -> List[Shelf]:
        """
        Filter shelves based on component requirements.
        
        Edge case 3: Restricted/Hazard-area components
        """
        candidates = []
        
        for shelf in all_shelves:
            # Check basic constraints
            can_store, reason = shelf.can_store(component)
            if not can_store:
                continue
            
            # Check zone preference
            if preferred_zones:
                if shelf.location.zone not in preferred_zones:
                    continue
            
            # Check if restricted
            if shelf.is_restricted:
                continue
            
            candidates.append(shelf)
        
        return candidates
    
    def _rule_based_score(
        self,
        features: Dict[str, float],
        component: Component,
        shelf: Shelf
    ) -> float:
        """
        Fallback rule-based scoring when ML model is not available.
        
        Uses weighted combination of features.
        """
        weights = {
            'usage_frequency': 0.15,
            'category_similarity': 0.10,
            'shelf_proximity': -0.20,  # Negative: closer is better
            'pathway_congestion': -0.15,  # Negative: less congestion is better
            'space_availability': 0.20,
            'distance_to_entrance': -0.10,
            'shelf_congestion_score': -0.10,
            'is_hazardous_match': 0.10,
            'climate_control_match': 0.10,
            'weight_utilization': -0.05,  # Negative: less utilization is better
            'volume_utilization': -0.05,
            'zone_preference': 0.10,
        }
        
        score = 0.0
        for feature_name, weight in weights.items():
            value = features.get(feature_name, 0.0)
            score += weight * value
        
        # Normalize to 0-1 range
        score = max(0.0, min(1.0, (score + 1.0) / 2.0))
        
        return score
    
    def _generate_reasoning(
        self,
        prediction: Dict,
        component: Component,
        shelf: Shelf
    ) -> str:
        """Generate human-readable reasoning for the prediction."""
        features = prediction['features']
        reasons = []
        
        if features.get('category_similarity', 0) > 0.5:
            reasons.append("Similar components stored here")
        
        if features.get('space_availability', 0) > 0.7:
            reasons.append("Good space availability")
        
        if features.get('pathway_congestion', 0) < 0.3:
            reasons.append("Low pathway congestion")
        
        if features.get('shelf_proximity', 100) < 20:
            reasons.append("Close to warehouse entrance")
        
        if features.get('zone_preference', 0) > 0.5:
            reasons.append("Matches historical zone preference")
        
        if not reasons:
            reasons.append("Best available option based on multiple factors")
        
        return "; ".join(reasons)

