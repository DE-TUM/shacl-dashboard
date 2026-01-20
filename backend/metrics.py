"""
Prometheus Metrics Module

This module provides Prometheus metrics for monitoring application performance,
query execution times, error rates, and endpoint usage.

Key Metrics:
- Request count by endpoint and status code
- Request duration histogram
- SPARQL query execution time
- Error count by type
- Cache hit/miss ratio
- Active requests gauge

Usage:
    from metrics import track_request, track_sparql_query
    
    with track_request('/api/v1/shapes'):
        # Handle request
        pass
    
    with track_sparql_query('get_shapes'):
        # Execute SPARQL query
        pass
"""

import time
import logging
from contextlib import contextmanager
from typing import Optional
from functools import wraps

logger = logging.getLogger(__name__)

# Try to import Prometheus client
try:
    from prometheus_client import (
        Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.warning("prometheus_client not installed. Metrics collection disabled.")
    PROMETHEUS_AVAILABLE = False


class MetricsManager:
    """
    Manager for Prometheus metrics with graceful degradation if Prometheus is not available.
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize metrics manager.
        
        Args:
            enabled: Whether metrics collection is enabled
        """
        self.enabled = enabled and PROMETHEUS_AVAILABLE
        
        if self.enabled:
            self._initialize_metrics()
        
        logger.info(
            "Metrics manager initialized",
            extra={'enabled': self.enabled, 'prometheus_available': PROMETHEUS_AVAILABLE}
        )
    
    def _initialize_metrics(self):
        """Initialize all Prometheus metrics."""
        # HTTP Request metrics
        self.http_requests_total = Counter(
            'shacl_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.http_request_duration_seconds = Histogram(
            'shacl_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
        )
        
        self.http_requests_in_progress = Gauge(
            'shacl_http_requests_in_progress',
            'Number of HTTP requests currently being processed',
            ['method', 'endpoint']
        )
        
        # SPARQL Query metrics
        self.sparql_queries_total = Counter(
            'shacl_sparql_queries_total',
            'Total SPARQL queries executed',
            ['operation', 'status']
        )
        
        self.sparql_query_duration_seconds = Histogram(
            'shacl_sparql_query_duration_seconds',
            'SPARQL query execution time in seconds',
            ['operation'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
        )
        
        # Error metrics
        self.errors_total = Counter(
            'shacl_errors_total',
            'Total errors by type',
            ['error_type', 'endpoint']
        )
        
        # Cache metrics
        self.cache_operations_total = Counter(
            'shacl_cache_operations_total',
            'Total cache operations',
            ['operation', 'result']  # operation: get/set/delete, result: hit/miss/success/error
        )
        
        # Application info
        self.app_info = Gauge(
            'shacl_app_info',
            'Application information',
            ['version', 'python_version']
        )
        
        logger.debug("Prometheus metrics initialized")
    
    def track_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """
        Record HTTP request metrics.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Request endpoint
            status: HTTP status code
            duration: Request duration in seconds
        """
        if not self.enabled:
            return
        
        try:
            self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
            self.http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
        except Exception as e:
            logger.error("Failed to track HTTP request metrics: %s", e)
    
    @contextmanager
    def track_request_in_progress(self, method: str, endpoint: str):
        """
        Context manager to track requests in progress.
        
        Args:
            method: HTTP method
            endpoint: Request endpoint
        """
        if self.enabled:
            try:
                self.http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
            except Exception as e:
                logger.error("Failed to increment in-progress metric: %s", e)
        
        try:
            yield
        finally:
            if self.enabled:
                try:
                    self.http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
                except Exception as e:
                    logger.error("Failed to decrement in-progress metric: %s", e)
    
    def track_sparql_query(self, operation: str, duration: float, success: bool = True):
        """
        Record SPARQL query metrics.
        
        Args:
            operation: Operation name
            duration: Query duration in seconds
            success: Whether the query succeeded
        """
        if not self.enabled:
            return
        
        try:
            status = 'success' if success else 'failure'
            self.sparql_queries_total.labels(operation=operation, status=status).inc()
            self.sparql_query_duration_seconds.labels(operation=operation).observe(duration)
        except Exception as e:
            logger.error("Failed to track SPARQL query metrics: %s", e)
    
    def track_error(self, error_type: str, endpoint: str):
        """
        Record error metrics.
        
        Args:
            error_type: Type of error (e.g., 'ValidationError', 'QueryExecutionError')
            endpoint: Endpoint where error occurred
        """
        if not self.enabled:
            return
        
        try:
            self.errors_total.labels(error_type=error_type, endpoint=endpoint).inc()
        except Exception as e:
            logger.error("Failed to track error metrics: %s", e)
    
    def track_cache_operation(self, operation: str, result: str):
        """
        Record cache operation metrics.
        
        Args:
            operation: Operation type ('get', 'set', 'delete')
            result: Result of operation ('hit', 'miss', 'success', 'error')
        """
        if not self.enabled:
            return
        
        try:
            self.cache_operations_total.labels(operation=operation, result=result).inc()
        except Exception as e:
            logger.error("Failed to track cache metrics: %s", e)
    
    def set_app_info(self, version: str, python_version: str):
        """
        Set application info metric.
        
        Args:
            version: Application version
            python_version: Python version
        """
        if not self.enabled:
            return
        
        try:
            self.app_info.labels(version=version, python_version=python_version).set(1)
        except Exception as e:
            logger.error("Failed to set app info: %s", e)
    
    def generate_metrics(self):
        """
        Generate metrics in Prometheus text format.
        
        Returns:
            Tuple of (metrics_text, content_type)
        """
        if not self.enabled:
            return "# Metrics collection is disabled\n", "text/plain"
        
        try:
            return generate_latest(), CONTENT_TYPE_LATEST
        except Exception as e:
            logger.error("Failed to generate metrics: %s", e)
            return f"# Error generating metrics: {e}\n", "text/plain"


# Global metrics manager instance
_metrics_manager: Optional[MetricsManager] = None


def get_metrics_manager() -> MetricsManager:
    """
    Get the global metrics manager instance.
    
    Returns:
        The global MetricsManager instance
    """
    global _metrics_manager
    if _metrics_manager is None:
        from config import Config
        metrics_enabled = getattr(Config, 'METRICS_ENABLED', True)
        _metrics_manager = MetricsManager(enabled=metrics_enabled)
        
        # Set application info
        try:
            import sys
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            _metrics_manager.set_app_info(version="1.0.0", python_version=python_version)
        except Exception as e:
            logger.error("Failed to set app info: %s", e)
    
    return _metrics_manager


@contextmanager
def track_sparql_query_time(operation: str):
    """
    Context manager to track SPARQL query execution time.
    
    Args:
        operation: Operation name
        
    Usage:
        with track_sparql_query_time('get_shapes'):
            results = execute_query(...)
    """
    metrics = get_metrics_manager()
    start_time = time.time()
    success = True
    
    try:
        yield
    except Exception:
        success = False
        raise
    finally:
        duration = time.time() - start_time
        metrics.track_sparql_query(operation, duration, success)


def track_request_metrics(func):
    """
    Decorator to automatically track request metrics for Flask routes.
    
    Usage:
        @app.route('/api/shapes')
        @track_request_metrics
        def get_shapes():
            return jsonify(...)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        
        metrics = get_metrics_manager()
        method = request.method
        endpoint = request.path
        
        start_time = time.time()
        status = 500  # Default to error
        
        with metrics.track_request_in_progress(method, endpoint):
            try:
                response = func(*args, **kwargs)
                
                # Extract status code from response
                if isinstance(response, tuple):
                    status = response[1] if len(response) > 1 else 200
                else:
                    status = 200
                
                return response
            except Exception as e:
                # Track error
                error_type = type(e).__name__
                metrics.track_error(error_type, endpoint)
                raise
            finally:
                duration = time.time() - start_time
                metrics.track_http_request(method, endpoint, status, duration)
    
    return wrapper
