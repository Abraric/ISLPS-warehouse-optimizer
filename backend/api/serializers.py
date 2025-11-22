"""
DRF serializers for API endpoints.
"""
from rest_framework import serializers
from .models import Component, Shelf, MovementLog, ModelPerformance, Location


class LocationSerializer(serializers.Serializer):
    """Serializer for location coordinates."""
    x = serializers.FloatField()
    y = serializers.FloatField()
    z = serializers.FloatField()
    zone = serializers.CharField(max_length=10)
    
    def to_representation(self, instance):
        """Convert Location embedded document to dict."""
        if isinstance(instance, Location):
            return {
                'x': instance.x,
                'y': instance.y,
                'z': instance.z,
                'zone': instance.zone,
            }
        return super().to_representation(instance)


class ComponentSerializer(serializers.Serializer):
    """Serializer for Component model."""
    component_id = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    weight_kg = serializers.FloatField(min_value=0)
    length_m = serializers.FloatField(min_value=0)
    width_m = serializers.FloatField(min_value=0)
    height_m = serializers.FloatField(min_value=0)
    
    is_hazardous = serializers.BooleanField(default=False)
    requires_climate_control = serializers.BooleanField(default=False)
    temperature_range = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        allow_null=True
    )
    
    total_retrievals = serializers.IntegerField(read_only=True)
    last_retrieved_at = serializers.DateTimeField(read_only=True, allow_null=True)
    avg_retrieval_frequency = serializers.FloatField(read_only=True)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def to_representation(self, instance):
        """Convert Component document to dict."""
        if isinstance(instance, Component):
            return {
                'component_id': instance.component_id,
                'name': instance.name,
                'category': instance.category,
                'description': getattr(instance, 'description', ''),
                'weight_kg': instance.weight_kg,
                'length_m': instance.length_m,
                'width_m': instance.width_m,
                'height_m': instance.height_m,
                'is_hazardous': instance.is_hazardous,
                'requires_climate_control': instance.requires_climate_control,
                'temperature_range': getattr(instance, 'temperature_range', None),
                'total_retrievals': instance.total_retrievals,
                'last_retrieved_at': instance.last_retrieved_at.isoformat() if instance.last_retrieved_at else None,
                'avg_retrieval_frequency': instance.avg_retrieval_frequency,
                'created_at': instance.created_at.isoformat() if instance.created_at else None,
                'updated_at': instance.updated_at.isoformat() if instance.updated_at else None,
            }
        return super().to_representation(instance)
    
    def create(self, validated_data):
        """Create a new Component instance."""
        return Component(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing Component instance."""
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class ShelfSerializer(serializers.Serializer):
    """Serializer for Shelf model."""
    shelf_id = serializers.CharField(max_length=100)
    location = LocationSerializer()
    
    max_weight_kg = serializers.FloatField(min_value=0)
    max_volume_m3 = serializers.FloatField(min_value=0)
    current_weight_kg = serializers.FloatField(read_only=True)
    current_volume_m3 = serializers.FloatField(read_only=True)
    available_space_m3 = serializers.FloatField(read_only=True)
    
    is_hazardous_zone = serializers.BooleanField(default=False)
    has_climate_control = serializers.BooleanField(default=False)
    temperature_range = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        allow_null=True
    )
    
    adjacent_shelves = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    distance_to_entrance = serializers.FloatField(min_value=0)
    
    current_congestion_score = serializers.FloatField(read_only=True)
    avg_retrieval_time_seconds = serializers.FloatField(read_only=True)
    retrieval_count_today = serializers.IntegerField(read_only=True)
    
    is_available = serializers.BooleanField(default=True)
    is_restricted = serializers.BooleanField(default=False)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def to_representation(self, instance):
        """Convert Shelf document to dict."""
        if isinstance(instance, Shelf):
            return {
                'shelf_id': instance.shelf_id,
                'location': LocationSerializer().to_representation(instance.location),
                'max_weight_kg': instance.max_weight_kg,
                'max_volume_m3': instance.max_volume_m3,
                'current_weight_kg': instance.current_weight_kg,
                'current_volume_m3': instance.current_volume_m3,
                'available_space_m3': getattr(instance, 'available_space_m3', 0),
                'is_hazardous_zone': instance.is_hazardous_zone,
                'has_climate_control': instance.has_climate_control,
                'temperature_range': getattr(instance, 'temperature_range', None),
                'adjacent_shelves': getattr(instance, 'adjacent_shelves', []),
                'distance_to_entrance': instance.distance_to_entrance,
                'current_congestion_score': instance.current_congestion_score,
                'avg_retrieval_time_seconds': instance.avg_retrieval_time_seconds,
                'retrieval_count_today': instance.retrieval_count_today,
                'is_available': instance.is_available,
                'is_restricted': instance.is_restricted,
                'created_at': instance.created_at.isoformat() if instance.created_at else None,
                'updated_at': instance.updated_at.isoformat() if instance.updated_at else None,
            }
        return super().to_representation(instance)
    
    def create(self, validated_data):
        """Create a new Shelf instance."""
        location_data = validated_data.pop('location')
        location = Location(**location_data)
        validated_data['location'] = location
        return Shelf(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing Shelf instance."""
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            location = Location(**location_data)
            instance.location = location
        
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class MovementLogSerializer(serializers.Serializer):
    """Serializer for MovementLog model."""
    log_id = serializers.CharField(read_only=True)
    component_id = serializers.CharField()
    shelf_id = serializers.CharField()
    movement_type = serializers.ChoiceField(choices=['STORAGE', 'RETRIEVAL'])
    timestamp = serializers.DateTimeField(required=False)
    duration_seconds = serializers.FloatField(required=False, allow_null=True)
    operator_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    congestion_at_time = serializers.FloatField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    def to_representation(self, instance):
        """Convert MovementLog document to dict."""
        if isinstance(instance, MovementLog):
            return {
                'log_id': instance.log_id,
                'component_id': instance.component_id,
                'shelf_id': instance.shelf_id,
                'movement_type': instance.movement_type,
                'timestamp': instance.timestamp.isoformat() if instance.timestamp else None,
                'duration_seconds': getattr(instance, 'duration_seconds', None),
                'operator_id': getattr(instance, 'operator_id', None),
                'congestion_at_time': getattr(instance, 'congestion_at_time', None),
                'created_at': instance.created_at.isoformat() if instance.created_at else None,
            }
        return super().to_representation(instance)
    
    def create(self, validated_data):
        """Create a new MovementLog instance."""
        return MovementLog(**validated_data)


class PredictionRequestSerializer(serializers.Serializer):
    """Serializer for prediction endpoint request."""
    component_id = serializers.CharField(required=True)
    consider_congestion = serializers.BooleanField(default=True)
    preferred_zones = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )


class PredictionResponseSerializer(serializers.Serializer):
    """Serializer for prediction endpoint response."""
    component_id = serializers.CharField()
    recommended_shelf_id = serializers.CharField()
    confidence_score = serializers.FloatField()
    alternative_shelves = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    reasoning = serializers.CharField()
    feature_vector = serializers.DictField(required=False)
