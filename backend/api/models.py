"""
MongoDB models for ASLPS using mongoengine.

Defines Component, Shelf, MovementLog, and related models.
"""
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime
import uuid


class Location(EmbeddedDocument):
    """Embedded document for 3D warehouse coordinates."""
    x = fields.FloatField(required=True, help_text="X coordinate (meters)")
    y = fields.FloatField(required=True, help_text="Y coordinate (meters)")
    z = fields.FloatField(required=True, help_text="Z coordinate (meters)")
    zone = fields.StringField(required=True, help_text="Zone identifier (A, B, C, etc.)")


class Component(Document):
    """
    Industrial component model.
    
    Stores component metadata including category, dimensions, and special requirements.
    """
    component_id = fields.StringField(required=True, unique=True, help_text="Unique component identifier")
    name = fields.StringField(required=True, max_length=200)
    category = fields.StringField(required=True, help_text="Component category for similarity matching")
    description = fields.StringField()
    
    # Physical attributes
    weight_kg = fields.FloatField(required=True, help_text="Weight in kilograms")
    length_m = fields.FloatField(required=True, help_text="Length in meters")
    width_m = fields.FloatField(required=True, help_text="Width in meters")
    height_m = fields.FloatField(required=True, help_text="Height in meters")
    
    # Storage requirements
    is_hazardous = fields.BooleanField(default=False, help_text="Requires special handling")
    requires_climate_control = fields.BooleanField(default=False)
    temperature_range = fields.ListField(fields.FloatField(), help_text="[min_temp, max_temp]")
    
    # Usage statistics (for feature engineering)
    total_retrievals = fields.IntField(default=0, help_text="Total number of times retrieved")
    last_retrieved_at = fields.DateTimeField(help_text="Last retrieval timestamp")
    avg_retrieval_frequency = fields.FloatField(default=0.0, help_text="Average retrievals per day")
    
    # Metadata
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'components',
        'indexes': [
            'component_id',
            'category',
            'is_hazardous',
            ('category', 'is_hazardous'),
        ],
    }
    
    def save(self, *args, **kwargs):
        """Update timestamp on save."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class Shelf(Document):
    """
    Storage shelf/rack model.
    
    Represents a physical storage location in the warehouse with capacity and constraints.
    """
    shelf_id = fields.StringField(required=True, unique=True, help_text="Unique shelf identifier")
    location = fields.EmbeddedDocumentField(Location, required=True)
    
    # Capacity
    max_weight_kg = fields.FloatField(required=True, help_text="Maximum weight capacity")
    max_volume_m3 = fields.FloatField(required=True, help_text="Maximum volume capacity")
    current_weight_kg = fields.FloatField(default=0.0)
    current_volume_m3 = fields.FloatField(default=0.0)
    available_space_m3 = fields.FloatField(help_text="Available space in cubic meters")
    
    # Constraints
    is_hazardous_zone = fields.BooleanField(default=False, help_text="Can store hazardous materials")
    has_climate_control = fields.BooleanField(default=False)
    temperature_range = fields.ListField(fields.FloatField(), help_text="[min_temp, max_temp]")
    
    # Proximity graph (for path distance calculation)
    adjacent_shelves = fields.ListField(fields.StringField(), help_text="List of adjacent shelf IDs")
    distance_to_entrance = fields.FloatField(help_text="Distance to warehouse entrance (meters)")
    
    # Traffic metrics
    current_congestion_score = fields.FloatField(default=0.0, help_text="Current congestion (0-1)")
    avg_retrieval_time_seconds = fields.FloatField(default=0.0, help_text="Average retrieval time")
    retrieval_count_today = fields.IntField(default=0, help_text="Retrievals today")
    
    # Status
    is_available = fields.BooleanField(default=True, help_text="Available for new components")
    is_restricted = fields.BooleanField(default=False, help_text="Temporarily restricted")
    
    # Metadata
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'shelves',
        'indexes': [
            'shelf_id',
            'location.zone',
            'is_available',
            'is_hazardous_zone',
            ('location.zone', 'is_available'),
        ],
    }
    
    def save(self, *args, **kwargs):
        """Update timestamp and available space on save."""
        self.updated_at = datetime.utcnow()
        self.available_space_m3 = max(0, self.max_volume_m3 - self.current_volume_m3)
        return super().save(*args, **kwargs)
    
    def can_store(self, component):
        """
        Check if component can be stored in this shelf.
        
        Args:
            component: Component instance
            
        Returns:
            tuple: (can_store: bool, reason: str)
        """
        # Check weight capacity
        if self.current_weight_kg + component.weight_kg > self.max_weight_kg:
            return False, "Weight capacity exceeded"
        
        # Check volume capacity
        component_volume = component.length_m * component.width_m * component.height_m
        if self.current_volume_m3 + component_volume > self.max_volume_m3:
            return False, "Volume capacity exceeded"
        
        # Check hazardous zone requirement
        if component.is_hazardous and not self.is_hazardous_zone:
            return False, "Component requires hazardous zone"
        
        # Check climate control requirement
        if component.requires_climate_control and not self.has_climate_control:
            return False, "Component requires climate control"
        
        # Check temperature range
        if component.temperature_range and self.temperature_range:
            comp_min, comp_max = component.temperature_range
            shelf_min, shelf_max = self.temperature_range
            if not (shelf_min <= comp_min and comp_max <= shelf_max):
                return False, "Temperature range mismatch"
        
        # Check availability
        if not self.is_available or self.is_restricted:
            return False, "Shelf is not available"
        
        return True, "OK"


class MovementLog(Document):
    """
    Movement log for tracking component storage and retrieval.
    
    Used for feature engineering (usage frequency, congestion patterns).
    """
    log_id = fields.StringField(required=True, unique=True, default=lambda: str(uuid.uuid4()))
    component_id = fields.StringField(required=True)
    shelf_id = fields.StringField(required=True)
    
    # Movement type
    movement_type = fields.StringField(
        required=True,
        choices=['STORAGE', 'RETRIEVAL'],
        help_text="Type of movement"
    )
    
    # Timestamps
    timestamp = fields.DateTimeField(required=True, default=datetime.utcnow)
    duration_seconds = fields.FloatField(help_text="Time taken for movement")
    
    # Context
    operator_id = fields.StringField(help_text="Operator who performed the movement")
    congestion_at_time = fields.FloatField(help_text="Congestion score at movement time")
    
    # Metadata
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'movement_logs',
        'indexes': [
            'component_id',
            'shelf_id',
            'movement_type',
            'timestamp',
            ('component_id', 'timestamp'),
            ('shelf_id', 'timestamp'),
        ],
    }


class ModelPerformance(Document):
    """
    Model performance tracking for drift detection.
    
    Stores prediction accuracy metrics over time.
    """
    metric_id = fields.StringField(required=True, unique=True, default=lambda: str(uuid.uuid4()))
    model_version = fields.StringField(required=True)
    
    # Metrics
    accuracy = fields.FloatField(help_text="Prediction accuracy")
    precision = fields.FloatField(help_text="Precision score")
    recall = fields.FloatField(help_text="Recall score")
    f1_score = fields.FloatField(help_text="F1 score")
    
    # Sample info
    sample_size = fields.IntField(help_text="Number of predictions evaluated")
    evaluation_window_hours = fields.IntField(help_text="Time window for evaluation")
    
    # Timestamp
    evaluated_at = fields.DateTimeField(required=True, default=datetime.utcnow)
    
    meta = {
        'collection': 'model_performance',
        'indexes': [
            'model_version',
            'evaluated_at',
            ('model_version', 'evaluated_at'),
        ],
    }

