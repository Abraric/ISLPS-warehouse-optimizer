"""
Custom middleware for logging and monitoring.
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class LoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests with timing information.
    Helps monitor API performance and detect anomalies.
    """
    
    def process_request(self, request):
        """Store request start time."""
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log request details and response time."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            logger.info(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s - "
                f"IP: {self.get_client_ip(request)}"
            )
            
            # Log slow requests as warnings
            if duration > 1.0:
                logger.warning(
                    f"Slow request detected: {request.path} took {duration:.3f}s"
                )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

