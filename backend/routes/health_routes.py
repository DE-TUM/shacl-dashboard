from flask import Blueprint, jsonify, Response
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
"""

health_bp = Blueprint('health', __name__)


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
