"""
URL routing for API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),
    
    # Components
    path('components/', views.component_list_create, name='component_list_create'),
    path('components/<str:component_id>/', views.component_detail, name='component_detail'),
    
    # Shelves
    path('shelves/', views.shelf_list_create, name='shelf_list_create'),
    path('shelves/<str:shelf_id>/', views.shelf_detail, name='shelf_detail'),
    
    # Movement logs
    path('movements/', views.movement_log_list_create, name='movement_log_list_create'),
    
    # Model performance
    path('model-performance/', views.model_performance, name='model_performance'),
]

