"""
Health Check Routes with Flask-RESTX Documentation

This module provides documented health check endpoints using Flask-RESTX
for automatic OpenAPI/Swagger generation.

Endpoints:
- /health: Basic health check
- /health/ready: Readiness probe  
- /health/live: Liveness probe
"""

from flask import jsonify
from flask_restx import Resource, Namespace, fields
from SPARQLWrapper import SPARQLWrapper
from config import ENDPOINT_URL
import sys
import logging

logger = logging.getLogger(__name__)

# Create namespace for health endpoints
health_ns = Namespace('health', description='Health check and monitoring endpoints')

# Define response models
health_model = health_ns.model('Health', {
    'status': fields.String(required=True, description='Health status', example='healthy'),
    'service': fields.String(required=True, description='Service name', example='shacl-dashboard-backend'),
    'version': fields.String(required=True, description='API version', example='1.0.0'),
    'python_version': fields.String(required=True, description='Python version', example='3.11.0')
})

readiness_check_model = health_ns.model('ReadinessCheck', {
    'sparql_endpoint': fields.String(required=True, description='SPARQL endpoint status', enum=['healthy', 'unhealthy', 'unknown']),
    'application': fields.String(required=True, description='Application status', enum=['ready', 'not_ready'])
})

readiness_model = health_ns.model('Readiness', {
    'status': fields.String(required=True, description='Readiness status', enum=['ready', 'not_ready']),
    'checks': fields.Nested(readiness_check_model, required=True, description='Individual health checks')
})

readiness_error_model = health_ns.model('ReadinessError', {
    'status': fields.String(required=True, description='Readiness status', example='not_ready'),
    'checks': fields.Nested(readiness_check_model, required=True, description='Individual health checks'),
    'error': fields.String(required=True, description='Error message', example='SPARQL endpoint is not accessible')
})

liveness_model = health_ns.model('Liveness', {
    'status': fields.String(required=True, description='Liveness status', example='alive'),
    'service': fields.String(required=True, description='Service name', example='shacl-dashboard-backend')
})


@health_ns.route('')
class HealthCheck(Resource):
    """Basic health check endpoint"""
    
    @health_ns.doc('health_check',
        responses={
            200: ('Success', health_model),
        })
    @health_ns.marshal_with(health_model)
    def get(self):
        """
        Check if the service is running
        
        Returns a simple status indicating the application is running.
        This is a lightweight check that doesn't verify external dependencies.
        Use this endpoint for basic service discovery.
        """
        return {
            'status': 'healthy',
            'service': 'shacl-dashboard-backend',
            'version': '1.0.0',
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }, 200


@health_ns.route('/ready')
class ReadinessCheck(Resource):
    """Readiness probe endpoint"""
    
    @health_ns.doc('readiness_check',
        responses={
            200: ('Ready', readiness_model),
            503: ('Not Ready', readiness_error_model)
        })
    def get(self):
        """
        Check if the service is ready to accept traffic
        
        Verifies that all critical dependencies (SPARQL endpoint) are accessible.
        Load balancers and orchestration systems should use this endpoint
        to determine if the instance can receive traffic.
        
        Returns:
            200: Service is ready with all dependencies healthy
            503: Service is not ready (dependencies unavailable)
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
            return {
                'status': 'not_ready',
                'checks': checks,
                'error': 'SPARQL endpoint is not accessible'
            }, 503
        
        return {
            'status': 'ready',
            'checks': checks
        }, 200


@health_ns.route('/live')
class LivenessCheck(Resource):
    """Liveness probe endpoint"""
    
    @health_ns.doc('liveness_check',
        responses={
            200: ('Alive', liveness_model),
        })
    @health_ns.marshal_with(liveness_model)
    def get(self):
        """
        Check if the service is alive
        
        Indicates whether the application is running and not deadlocked.
        This is a simple check that the application process is alive.
        Orchestration systems should use this to determine if the instance
        should be restarted.
        """
        return {
            'status': 'alive',
            'service': 'shacl-dashboard-backend'
        }, 200
