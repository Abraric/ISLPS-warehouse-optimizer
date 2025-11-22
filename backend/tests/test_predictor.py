"""
Unit tests for ML predictor service.
"""
import pytest
from datetime import datetime, timedelta
from api.models import Component, Shelf, Location, MovementLog
from ml_service.predictor import LocationPredictor


@pytest.mark.django_db
class TestLocationPredictor:
    """Test LocationPredictor."""
    
    def setup_method(self):
        """Set up test data."""
        # Create test component
        self.component = Component(
            component_id='TEST-COMP-001',
            name='Test Component',
            category='Test',
            weight_kg=10.0,
            length_m=1.0,
            width_m=0.5,
            height_m=0.2,
        )
        self.component.save()
        
        # Create test shelves
        self.shelf1 = Shelf(
            shelf_id='SHELF-TEST-001',
            location=Location(x=10.0, y=20.0, z=5.0, zone='A'),
            max_weight_kg=100.0,
            max_volume_m3=10.0,
            distance_to_entrance=10.0,
            is_available=True,
        )
        self.shelf1.save()
        
        self.shelf2 = Shelf(
            shelf_id='SHELF-TEST-002',
            location=Location(x=20.0, y=30.0, z=5.0, zone='B'),
            max_weight_kg=200.0,
            max_volume_m3=20.0,
            distance_to_entrance=25.0,
            is_available=True,
        )
        self.shelf2.save()
    
    def test_predictor_initialization(self):
        """Test predictor initialization."""
        predictor = LocationPredictor()
        assert predictor.feature_engineer is not None
        assert len(predictor.feature_names) > 0
    
    def test_predict_with_valid_component(self):
        """Test prediction with valid component."""
        predictor = LocationPredictor()
        result = predictor.predict('TEST-COMP-001')
        
        assert 'recommended_shelf_id' in result or 'error' in result
        if 'recommended_shelf_id' in result:
            assert result['recommended_shelf_id'] in ['SHELF-TEST-001', 'SHELF-TEST-002']
            assert 'confidence_score' in result
    
    def test_predict_with_invalid_component(self):
        """Test prediction with invalid component."""
        predictor = LocationPredictor()
        result = predictor.predict('INVALID-COMP')
        
        assert 'error' in result
        assert result['recommended_shelf_id'] is None
    
    def test_predict_with_no_available_shelves(self):
        """Test prediction when no shelves are available."""
        # Mark all shelves as unavailable
        Shelf.objects.update(is_available=False)
        
        predictor = LocationPredictor()
        result = predictor.predict('TEST-COMP-001')
        
        assert 'error' in result
        assert 'No available shelves' in result['error']

