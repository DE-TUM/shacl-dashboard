"""
Flask-RESTX API Configuration Module

This module configures Flask-RESTX for automatic OpenAPI/Swagger documentation
generation. It provides a centralized API configuration that all routes can use.

Features:
- Automatic OpenAPI 3.0 specification generation
- Interactive Swagger UI at /api/v1/docs
- Request/response validation
- Standardized error handling
- API versioning support

Usage:
    from app_api import api, create_namespace
    
    # Create a namespace for your routes
    shapes_ns = create_namespace(
        'shapes',
        description='Shape-related operations'
    )
    
    @shapes_ns.route('/count')
    class ShapeCount(Resource):
        @shapes_ns.doc('get_shape_count')
        @shapes_ns.marshal_with(count_response_model)
        def get(self):
            '''Get count of shapes'''
            return {'count': 42}
"""

from flask import Blueprint
from flask_restx import Api
from typing import Optional


# Create a blueprint for the API
api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

# Configure Flask-RESTX API with OpenAPI documentation
api = Api(
    api_blueprint,
    version='1.0.0',
    title='SHACL Dashboard API',
    description='''
    RESTful API for the SHACL Dashboard application.
    
    This API provides endpoints for querying SHACL validation reports,
    analyzing shapes, and retrieving statistics about RDF data quality.
    
    ## Features
    - Query validation reports and shapes
    - Retrieve violation statistics
    - Analyze constraint components
    - Get detailed shape information
    - Health and readiness checks
    
    ## Authentication
    Currently, no authentication is required for API access.
    
    ## Rate Limiting
    Rate limiting is not yet implemented but is planned for future releases.
    
    ## Error Handling
    All errors follow a standardized format with error codes and messages.
    See the Error Models section for details.
    
    ## Graph URIs
    Most endpoints accept `graph_uri` parameters. The default values are:
    - Validation Report: `http://ex.org/ValidationReport`
    - Shapes Graph: `http://ex.org/ShapesGraph`
    
    ## Pagination
    Endpoints that return lists support pagination via `limit` and `offset` parameters.
    ''',
    doc='/docs',  # Swagger UI will be at /api/v1/docs
    validate=True,  # Enable request validation
    catch_all_404s=True,
    contact='SHACL Dashboard Team',
    license='MIT',
    license_url='https://opensource.org/licenses/MIT'
)


# Import and register documented namespaces
from routes.health_routes_documented import health_ns
api.add_namespace(health_ns, path='/health')


# Custom error handlers for Flask-RESTX
@api.errorhandler(Exception)
def handle_exception(error):
    """Handle unexpected exceptions with proper error response."""
    from error_codes import format_error_response, ErrorCodes
    return format_error_response(
        ErrorCodes.SYS_INTERNAL_ERROR,
        details=str(error)
    ), 500


@api.errorhandler(ValueError)
def handle_value_error(error):
    """Handle ValueError with validation error response."""
    from error_codes import format_error_response, ErrorCodes
    return format_error_response(
        ErrorCodes.VAL_INVALID_PARAMETER,
        details=str(error)
    ), 400


def create_namespace(name: str, description: str, path: Optional[str] = None):
    """
    Create and register a new namespace for API endpoints.
    
    Args:
        name: Name of the namespace (e.g., 'shapes', 'validation')
        description: Description of the namespace functionality
        path: Optional custom path (defaults to '/{name}')
        
    Returns:
        Namespace: Flask-RESTX namespace for organizing routes
        
    Example:
        shapes_ns = create_namespace('shapes', 'Shape operations')
        
        @shapes_ns.route('/count')
        class ShapeCount(Resource):
            def get(self):
                return {'count': 42}
    """
    if path is None:
        path = f'/{name}'
    
    return api.namespace(
        name,
        description=description,
        path=path
    )


# Helper function to register common response codes
def add_standard_responses(route_decorator):
    """
    Add standard response documentation to an endpoint.
    
    Args:
        route_decorator: Flask-RESTX route decorator
        
    Returns:
        Decorated route with standard responses
        
    Example:
        @shapes_ns.route('/count')
        class ShapeCount(Resource):
            @add_standard_responses
            @shapes_ns.doc('get_count')
            def get(self):
                return {'count': 42}
    """
    responses = {
        200: 'Success',
        400: ('Validation Error', 'error'),
        404: ('Resource Not Found', 'error'),
        500: ('Internal Server Error', 'error')
    }
    
    for code, response in responses.items():
        if isinstance(response, tuple):
            description, model_name = response
            route_decorator = route_decorator.doc(responses={code: (description, model_name)})
        else:
            route_decorator = route_decorator.doc(responses={code: response})
    
    return route_decorator
