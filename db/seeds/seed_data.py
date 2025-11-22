"""
Seed data script for ASLPS MongoDB database.

Creates sample components, shelves, and movement logs for testing and development.
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from api.models import Component, Shelf, Location, MovementLog


def create_components():
    """Create sample components."""
    print("Creating sample components...")
    
    components_data = [
        {
            'component_id': 'COMP-001',
            'name': 'Steel Bearing 6205',
            'category': 'Mechanical',
            'description': 'Standard ball bearing',
            'weight_kg': 0.5,
            'length_m': 0.05,
            'width_m': 0.05,
            'height_m': 0.02,
            'is_hazardous': False,
            'requires_climate_control': False,
        },
        {
            'component_id': 'COMP-002',
            'name': 'Electronic Control Board',
            'category': 'Electronics',
            'description': 'Main control board for assembly line',
            'weight_kg': 2.5,
            'length_m': 0.3,
            'width_m': 0.2,
            'height_m': 0.05,
            'is_hazardous': False,
            'requires_climate_control': True,
            'temperature_range': [15.0, 25.0],
        },
        {
            'component_id': 'COMP-003',
            'name': 'Chemical Solvent A',
            'category': 'Chemical',
            'description': 'Industrial cleaning solvent',
            'weight_kg': 10.0,
            'length_m': 0.4,
            'width_m': 0.3,
            'height_m': 0.3,
            'is_hazardous': True,
            'requires_climate_control': False,
        },
        {
            'component_id': 'COMP-004',
            'name': 'Raw Steel Sheet',
            'category': 'Raw Materials',
            'description': '1m x 2m steel sheet',
            'weight_kg': 50.0,
            'length_m': 2.0,
            'width_m': 1.0,
            'height_m': 0.01,
            'is_hazardous': False,
            'requires_climate_control': False,
        },
        {
            'component_id': 'COMP-005',
            'name': 'Finished Product Box',
            'category': 'Finished Goods',
            'description': 'Packaged finished product',
            'weight_kg': 5.0,
            'length_m': 0.5,
            'width_m': 0.4,
            'height_m': 0.3,
            'is_hazardous': False,
            'requires_climate_control': False,
        },
    ]
    
    # Add more components
    for i in range(6, 21):
        category = random.choice(['Mechanical', 'Electronics', 'Chemical', 'Raw Materials', 'Finished Goods'])
        components_data.append({
            'component_id': f'COMP-{i:03d}',
            'name': f'Sample Component {i}',
            'category': category,
            'description': f'Sample {category} component',
            'weight_kg': random.uniform(0.5, 50.0),
            'length_m': random.uniform(0.1, 2.0),
            'width_m': random.uniform(0.1, 1.0),
            'height_m': random.uniform(0.01, 0.5),
            'is_hazardous': random.choice([True, False]) if category == 'Chemical' else False,
            'requires_climate_control': random.choice([True, False]) if category == 'Electronics' else False,
        })
    
    created = 0
    for comp_data in components_data:
        try:
            Component.objects.get(component_id=comp_data['component_id'])
            print(f"  Component {comp_data['component_id']} already exists")
        except Component.DoesNotExist:
            Component(**comp_data).save()
            created += 1
    
    print(f"Created {created} new components. Total: {Component.objects.count()}")


def create_shelves():
    """Create sample shelves with proximity graph."""
    print("\nCreating sample shelves...")
    
    zones = ['A', 'B', 'C', 'D', 'E']
    shelves_data = []
    
    # Create shelves in a grid pattern
    shelf_id = 1
    for zone in zones:
        for row in range(1, 5):  # 4 rows per zone
            for col in range(1, 4):  # 3 columns per row
                shelf_id_str = f'SHELF-{zone}-{row:02d}-{col:02d}'
                
                # Calculate distance to entrance (zone A, row 1 is closest)
                if zone == 'A' and row == 1:
                    distance = 5.0 + (col - 1) * 2.0
                else:
                    zone_dist = (ord(zone) - ord('A')) * 20.0
                    row_dist = (row - 1) * 5.0
                    col_dist = (col - 1) * 2.0
                    distance = 5.0 + zone_dist + row_dist + col_dist
                
                # Determine adjacent shelves
                adjacent = []
                if col > 1:
                    adjacent.append(f'SHELF-{zone}-{row:02d}-{col-1:02d}')
                if col < 3:
                    adjacent.append(f'SHELF-{zone}-{row:02d}-{col+1:02d}')
                if row > 1:
                    adjacent.append(f'SHELF-{zone}-{row-1:02d}-{col:02d}')
                if row < 4:
                    adjacent.append(f'SHELF-{zone}-{row+1:02d}-{col:02d}')
                
                # Some shelves have special properties
                is_hazardous_zone = (zone == 'C' and row >= 3)  # Zone C, rows 3-4 are hazardous
                has_climate_control = (zone == 'B')  # Zone B has climate control
                
                location = Location(
                    x=float(col * 2.0),
                    y=float(row * 3.0),
                    z=float((ord(zone) - ord('A')) * 2.0),
                    zone=zone
                )
                
                shelves_data.append({
                    'shelf_id': shelf_id_str,
                    'location': location,
                    'max_weight_kg': random.uniform(100.0, 500.0),
                    'max_volume_m3': random.uniform(5.0, 20.0),
                    'current_weight_kg': random.uniform(0.0, 200.0),
                    'current_volume_m3': random.uniform(0.0, 10.0),
                    'is_hazardous_zone': is_hazardous_zone,
                    'has_climate_control': has_climate_control,
                    'temperature_range': [15.0, 25.0] if has_climate_control else None,
                    'adjacent_shelves': adjacent,
                    'distance_to_entrance': distance,
                    'is_available': random.choice([True, True, True, False]),  # 75% available
                    'is_restricted': random.choice([True, False, False, False, False]),  # 20% restricted
                })
    
    created = 0
    for shelf_data in shelves_data:
        try:
            Shelf.objects.get(shelf_id=shelf_data['shelf_id'])
            print(f"  Shelf {shelf_data['shelf_id']} already exists")
        except Shelf.DoesNotExist:
            Shelf(**shelf_data).save()
            created += 1
    
    print(f"Created {created} new shelves. Total: {Shelf.objects.count()}")


def create_movement_logs():
    """Create sample movement logs for training and testing."""
    print("\nCreating sample movement logs...")
    
    components = list(Component.objects.all())
    shelves = list(Shelf.objects.filter(is_available=True))
    
    if not components or not shelves:
        print("  No components or shelves available. Skipping movement logs.")
        return
    
    # Create logs for the past 30 days
    now = datetime.utcnow()
    logs_created = 0
    
    for day in range(30):
        date = now - timedelta(days=day)
        
        # Create 10-50 movements per day
        num_movements = random.randint(10, 50)
        
        for _ in range(num_movements):
            component = random.choice(components)
            shelf = random.choice(shelves)
            
            # Random time during the day
            hour = random.randint(6, 20)
            minute = random.randint(0, 59)
            timestamp = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Movement type (60% storage, 40% retrieval)
            movement_type = random.choice(['STORAGE', 'STORAGE', 'STORAGE', 'RETRIEVAL', 'RETRIEVAL'])
            
            # Duration (storage takes longer)
            if movement_type == 'STORAGE':
                duration = random.uniform(120.0, 300.0)  # 2-5 minutes
            else:
                duration = random.uniform(60.0, 180.0)  # 1-3 minutes
            
            # Congestion score (higher during peak hours 9-11, 14-16)
            peak_hour = hour in [9, 10, 11, 14, 15, 16]
            congestion = random.uniform(0.3, 0.9) if peak_hour else random.uniform(0.0, 0.5)
            
            log = MovementLog(
                component_id=component.component_id,
                shelf_id=shelf.shelf_id,
                movement_type=movement_type,
                timestamp=timestamp,
                duration_seconds=duration,
                operator_id=f'OP-{random.randint(1, 10):02d}',
                congestion_at_time=congestion,
            )
            log.save()
            logs_created += 1
    
    print(f"Created {logs_created} movement logs")


def main():
    """Main seeding function."""
    print("="*60)
    print("ASLPS Database Seeding")
    print("="*60)
    
    try:
        create_components()
        create_shelves()
        create_movement_logs()
        
        print("\n" + "="*60)
        print("Seeding completed successfully!")
        print("="*60)
        print(f"\nSummary:")
        print(f"  Components: {Component.objects.count()}")
        print(f"  Shelves: {Shelf.objects.count()}")
        print(f"  Movement Logs: {MovementLog.objects.count()}")
        
    except Exception as e:
        print(f"\nError during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

