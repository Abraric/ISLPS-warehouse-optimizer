"""
ML service views for prediction endpoint.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging

from .predictor import LocationPredictor
from api.serializers import PredictionRequestSerializer, PredictionResponseSerializer

logger = logging.getLogger(__name__)

# Initialize predictor (singleton)
_predictor = None


def get_predictor():
    """Get or create predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = LocationPredictor()
    return _predictor


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_location(request):
    """
    Predict optimal storage location for a component.
    
    POST /api/predict-location/
    
    Request body:
    {
        "component_id": "COMP-001",
        "consider_congestion": true,
        "preferred_zones": ["A", "B"]
    }
    
    Response:
    {
        "component_id": "COMP-001",
        "recommended_shelf_id": "SHELF-A-12",
        "confidence_score": 0.85,
        "alternative_shelves": [...],
        "reasoning": "...",
        "feature_vector": {...}
    }
    """
    serializer = PredictionRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    component_id = serializer.validated_data['component_id']
    consider_congestion = serializer.validated_data.get('consider_congestion', True)
    preferred_zones = serializer.validated_data.get('preferred_zones', [])
    
    try:
        predictor = get_predictor()
        result = predictor.predict(
            component_id=component_id,
            consider_congestion=consider_congestion,
            preferred_zones=preferred_zones if preferred_zones else None
        )
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log prediction for monitoring
        logger.info(
            f"Prediction made: component={component_id}, "
            f"shelf={result['recommended_shelf_id']}, "
            f"confidence={result['confidence_score']:.3f}"
        )
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Prediction failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

