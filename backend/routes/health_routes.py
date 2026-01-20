from flask import Blueprint, jsonify, Response, request
from SPARQLWrapper import SPARQLWrapper
from config import ENDPOINT_URL
import sys
import os
import logging

logger = logging.getLogger(__name__)

"""
Health Check Routes Module

This module provides health check endpoints for monitoring and observability.
These endpoints allow external monitoring systems to verify that the application
and its dependencies are functioning correctly.

Endpoints:
- /health: Basic health check for the application
- /health/ready: Readiness probe (checks if app can serve traffic)
- /health/live: Liveness probe (checks if app is running)
- /health/cache: Cache statistics and management
- /metrics: Prometheus metrics endpoint
"""

health_bp = Blueprint('health', __name__)


@health_bp.route('/metrics', methods=['GET'])
def metrics() -> Response:
    """
    Prometheus metrics endpoint.
    
    Returns Prometheus-formatted metrics for monitoring application performance.
    
    Metrics include:
    - HTTP request count and duration by endpoint
    - SPARQL query execution time by operation
    - Error counts by type
    - Cache hit/miss statistics
    - Active requests gauge
    
    Returns:
        Response: Prometheus text format metrics
    """
    try:
        from metrics import get_metrics_manager
        metrics_manager = get_metrics_manager()
        data, content_type = metrics_manager.generate_metrics()
        return Response(data, mimetype=content_type)
    except Exception as e:
        logger.error(f"Failed to generate metrics: {str(e)}")
        return Response(f"# Error generating metrics: {str(e)}\n", mimetype="text/plain")



@health_bp.route('/health', methods=['GET'])
def health_check() -> Response:
    """
    Basic health check endpoint.
    
    Returns a simple status indicating the application is running.
    This is a lightweight check that doesn't verify external dependencies.
    
    Returns:
        Response: JSON response with status and version information.
            Format: {'status': 'healthy', 'service': 'shacl-dashboard-backend', 'version': '1.0.0'}
    """
    return jsonify({
        'status': 'healthy',
        'service': 'shacl-dashboard-backend',
        'version': '1.0.0',
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }), 200


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check() -> Response:
    """
    Readiness probe endpoint.
    
    Checks if the application is ready to serve traffic by verifying
    that all critical dependencies (like the SPARQL endpoint) are accessible.
    
    This endpoint should be used by load balancers and orchestration systems
    to determine if the instance can receive traffic.
    
    Returns:
        Response: JSON response with readiness status and dependency checks.
            Format: {'status': 'ready'|'not_ready', 'checks': {...}}
            
    Status Codes:
        200: Application is ready to serve traffic
        503: Application is not ready (dependencies unavailable)
    """
    checks = {
        'sparql_endpoint': 'unknown',
        'application': 'ready'
    }
    
    # Check SPARQL endpoint connectivity
    try:
        sparql = SPARQLWrapper(ENDPOINT_URL)
        sparql.setQuery("ASK { ?s ?p ?o }")
        sparql.setTimeout(5)  # 5 second timeout
        result = sparql.query()
        checks['sparql_endpoint'] = 'healthy'
    except Exception as e:
        logger.error(f"SPARQL endpoint health check failed: {str(e)}")
        checks['sparql_endpoint'] = 'unhealthy'
        return jsonify({
            'status': 'not_ready',
            'checks': checks,
            'error': 'SPARQL endpoint is not accessible'
        }), 503
    
    return jsonify({
        'status': 'ready',
        'checks': checks
    }), 200


@health_bp.route('/health/live', methods=['GET'])
def liveness_check() -> Response:
    """
    Liveness probe endpoint.
    
    Indicates whether the application is running and not deadlocked.
    This is a simple check that the application process is alive.
    
    This endpoint should be used by orchestration systems to determine
    if the instance should be restarted.
    
    Returns:
        Response: JSON response with liveness status.
            Format: {'status': 'alive'}
    """
    return jsonify({
        'status': 'alive',
        'service': 'shacl-dashboard-backend'
    }), 200


@health_bp.route('/health/cache', methods=['GET'])
def cache_stats() -> Response:
    """
    Cache statistics endpoint.
    
    Returns statistics about the cache usage and configuration.
    
    Returns:
        Response: JSON response with cache statistics.
            Format: {'backend': 'memory'|'redis', 'enabled': true|false, 'entries': N, ...}
    """
    try:
        from cache_manager import get_cache_manager
        cache = get_cache_manager()
        stats = cache.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Failed to get cache stats: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve cache statistics',
            'details': str(e)
        }), 500


@health_bp.route('/health/cache/clear', methods=['POST'])
def clear_cache() -> Response:
    """
    Clear cache endpoint.
    
    Clears all or specific cache entries. Requires a pattern parameter
    to specify which entries to clear (default: 'shacl_cache:*').
    
    Query Parameters:
        pattern (optional): Pattern to match cache keys (default: 'shacl_cache:*')
    
    Returns:
        Response: JSON response with number of entries cleared.
            Format: {'status': 'cleared', 'count': N, 'pattern': '...'}
    """
    try:
        from cache_manager import get_cache_manager
        cache = get_cache_manager()
        
        if not cache.enabled:
            return jsonify({
                'status': 'disabled',
                'message': 'Caching is disabled'
            }), 200
        
        pattern = request.args.get('pattern', 'shacl_cache:*')
        count = cache.clear(pattern)
        
        return jsonify({
            'status': 'cleared',
            'count': count,
            'pattern': pattern
        }), 200
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        return jsonify({
            'error': 'Failed to clear cache',
            'details': str(e)
        }), 500

