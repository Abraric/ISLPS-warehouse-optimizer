"""
Unit tests for Django models.
"""
import pytest
from datetime import datetime
from api.models import Component, Shelf, Location, MovementLog


@pytest.mark.django_db
class TestComponent:
    """Test Component model."""
    
    def test_create_component(self):
        """Test creating a component."""
        component = Component(
            component_id='TEST-001',
            name='Test Component',
            category='Test',
            weight_kg=10.0,
            length_m=1.0,
            width_m=0.5,
            height_m=0.2,
        )
        component.save()
        
        assert component.component_id == 'TEST-001'
        assert component.name == 'Test Component'
        assert Component.objects.filter(component_id='TEST-001').exists()
    
    def test_component_timestamps(self):
        """Test component timestamp updates."""
        component = Component(
            component_id='TEST-002',
            name='Test',
            category='Test',
            weight_kg=10.0,
            length_m=1.0,
            width_m=0.5,
            height_m=0.2,
        )
        component.save()
        
        created_at = component.created_at
        updated_at = component.updated_at
        
        # Update component
        component.name = 'Updated'
        component.save()
        
        assert component.updated_at > updated_at


@pytest.mark.django_db
class TestShelf:
    """Test Shelf model."""
    
    def test_create_shelf(self):
        """Test creating a shelf."""
        location = Location(x=10.0, y=20.0, z=5.0, zone='A')
        shelf = Shelf(
            shelf_id='SHELF-TEST-001',
            location=location,
            max_weight_kg=100.0,
            max_volume_m3=10.0,
            distance_to_entrance=15.0,
        )
        shelf.save()
        
        assert shelf.shelf_id == 'SHELF-TEST-001'
        assert shelf.location.zone == 'A'
        assert shelf.available_space_m3 == 10.0
    
    def test_shelf_can_store(self):
        """Test shelf storage validation."""
        location = Location(x=10.0, y=20.0, z=5.0, zone='A')
        shelf = Shelf(
            shelf_id='SHELF-TEST-002',
            location=location,
            max_weight_kg=100.0,
            max_volume_m3=10.0,
            distance_to_entrance=15.0,
        )
        shelf.save()
        
        component = Component(
            component_id='TEST-003',
            name='Test',
            category='Test',
            weight_kg=50.0,
            length_m=1.0,
            width_m=1.0,
            height_m=1.0,
        )
        component.save()
        
        can_store, reason = shelf.can_store(component)
        assert can_store is True
        assert reason == 'OK'
        
        # Test weight limit
        component.weight_kg = 200.0
        can_store, reason = shelf.can_store(component)
        assert can_store is False
        assert 'Weight' in reason


@pytest.mark.django_db
class TestMovementLog:
    """Test MovementLog model."""
    
    def test_create_movement_log(self):
        """Test creating a movement log."""
        log = MovementLog(
            component_id='TEST-001',
            shelf_id='SHELF-001',
            movement_type='STORAGE',
            timestamp=datetime.utcnow(),
        )
        log.save()
        
        assert log.movement_type == 'STORAGE'
        assert MovementLog.objects.filter(component_id='TEST-001').exists()

