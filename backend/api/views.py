"""
API views for CRUD operations and health checks.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import Component, Shelf, MovementLog, ModelPerformance
from .serializers import (
    ComponentSerializer,
    ShelfSerializer,
    MovementLogSerializer,
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring.
    
    Returns:
        - 200: Service is healthy
        - 503: Service is unhealthy
    """
    try:
        # Check MongoDB connection
        Component.objects.first()
        
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'service': 'ASLPS Backend',
            'version': '1.0.0'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def component_list_create(request):
    """
    List all components or create a new component.
    
    GET: Returns paginated list of components
    POST: Creates a new component
    """
    if request.method == 'GET':
        components = Component.objects.all()
        serializer = ComponentSerializer(components, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = ComponentSerializer(data=request.data)
        if serializer.is_valid():
            component = serializer.save()
            logger.info(f"Created component: {component.component_id}")
            return Response(
                ComponentSerializer(component).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def component_detail(request, component_id):
    """
    Retrieve, update, or delete a specific component.
    """
    try:
        component = Component.objects.get(component_id=component_id)
    except Component.DoesNotExist:
        return Response(
            {'error': 'Component not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = ComponentSerializer(component)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = ComponentSerializer(component, data=request.data, partial=True)
        if serializer.is_valid():
            component = serializer.save()
            logger.info(f"Updated component: {component.component_id}")
            return Response(ComponentSerializer(component).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        component.delete()
        logger.info(f"Deleted component: {component_id}")
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def shelf_list_create(request):
    """
    List all shelves or create a new shelf.
    """
    if request.method == 'GET':
        shelves = Shelf.objects.all()
        serializer = ShelfSerializer(shelves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = ShelfSerializer(data=request.data)
        if serializer.is_valid():
            shelf = serializer.save()
            logger.info(f"Created shelf: {shelf.shelf_id}")
            return Response(
                ShelfSerializer(shelf).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def shelf_detail(request, shelf_id):
    """
    Retrieve, update, or delete a specific shelf.
    """
    try:
        shelf = Shelf.objects.get(shelf_id=shelf_id)
    except Shelf.DoesNotExist:
        return Response(
            {'error': 'Shelf not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = ShelfSerializer(shelf)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = ShelfSerializer(shelf, data=request.data, partial=True)
        if serializer.is_valid():
            shelf = serializer.save()
            logger.info(f"Updated shelf: {shelf.shelf_id}")
            return Response(ShelfSerializer(shelf).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        shelf.delete()
        logger.info(f"Deleted shelf: {shelf_id}")
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def movement_log_list_create(request):
    """
    List movement logs or create a new log entry.
    """
    if request.method == 'GET':
        # Optional filters
        component_id = request.query_params.get('component_id')
        shelf_id = request.query_params.get('shelf_id')
        hours = request.query_params.get('hours', 24)  # Default: last 24 hours
        
        logs = MovementLog.objects.all()
        
        if component_id:
            logs = logs.filter(component_id=component_id)
        if shelf_id:
            logs = logs.filter(shelf_id=shelf_id)
        
        # Filter by time window
        time_threshold = timezone.now() - timedelta(hours=int(hours))
        logs = logs.filter(timestamp__gte=time_threshold)
        
        serializer = MovementLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = MovementLogSerializer(data=request.data)
        if serializer.is_valid():
            log = serializer.save()
            logger.info(f"Created movement log: {log.log_id}")
            return Response(
                MovementLogSerializer(log).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def model_performance(request):
    """
    Get model performance metrics for monitoring.
    """
    version = request.query_params.get('version', 'latest')
    hours = int(request.query_params.get('hours', 168))  # Default: last week
    
    time_threshold = timezone.now() - timedelta(hours=hours)
    metrics = ModelPerformance.objects.filter(evaluated_at__gte=time_threshold)
    
    if version != 'latest':
        metrics = metrics.filter(model_version=version)
    
    metrics = metrics.order_by('-evaluated_at')
    
    # Aggregate latest metrics
    if metrics:
        latest = metrics.first()
        return Response({
            'model_version': latest.model_version,
            'accuracy': latest.accuracy,
            'precision': latest.precision,
            'recall': latest.recall,
            'f1_score': latest.f1_score,
            'sample_size': latest.sample_size,
            'evaluated_at': latest.evaluated_at.isoformat(),
            'history': [
                {
                    'evaluated_at': m.evaluated_at.isoformat(),
                    'accuracy': m.accuracy,
                    'f1_score': m.f1_score,
                }
                for m in metrics[:50]  # Last 50 records
            ]
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'No performance metrics available',
        'model_version': version
    }, status=status.HTTP_404_NOT_FOUND)

