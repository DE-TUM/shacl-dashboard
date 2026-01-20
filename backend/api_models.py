"""
API Models Module

This module defines all the Pydantic and Flask-RESTX models used for
API request/response validation and OpenAPI/Swagger documentation.

The models are organized by domain:
- Validation Report Models
- Shape Models
- Query Parameter Models
- Response Models
- Error Models

Usage:
    from api_models import graph_uri_model, error_model
    from flask_restx import Resource, Namespace
    
    ns = Namespace('shapes', description='Shape operations')
    
    @ns.route('/count')
    class ShapeCount(Resource):
        @ns.doc(responses={200: 'Success', 400: 'Validation Error'})
        @ns.expect(graph_uri_model)
        @ns.marshal_with(count_response_model)
        def get(self):
            pass
"""

from flask_restx import fields, Model
from typing import Dict, Any


# ==================== Input Models ====================

def create_input_models(api) -> Dict[str, Model]:
    """Create and register all input models with the API."""
    
    # Graph URI input model
    graph_uri_model = api.model('GraphURI', {
        'graph_uri': fields.String(
            required=False,
            description='URI of the RDF graph to query',
            example='http://ex.org/ValidationReport',
            default='http://ex.org/ValidationReport'
        )
    })
    
    # Shapes graph URI input model
    shapes_graph_model = api.model('ShapesGraph', {
        'shapes_graph_uri': fields.String(
            required=False,
            description='URI of the shapes graph',
            example='http://ex.org/ShapesGraph',
            default='http://ex.org/ShapesGraph'
        ),
        'validation_report_uri': fields.String(
            required=False,
            description='URI of the validation report graph',
            example='http://ex.org/ValidationReport',
            default='http://ex.org/ValidationReport'
        )
    })
    
    # Node shape input model
    node_shape_model = api.model('NodeShape', {
        'node_shape': fields.String(
            required=True,
            description='URI of the node shape',
            example='http://ex.org/PersonShape'
        ),
        'shapes_graph_uri': fields.String(
            required=False,
            description='URI of the shapes graph',
            default='http://ex.org/ShapesGraph'
        ),
        'validation_report_uri': fields.String(
            required=False,
            description='URI of the validation report graph',
            default='http://ex.org/ValidationReport'
        )
    })
    
    # Pagination input model
    pagination_model = api.model('Pagination', {
        'limit': fields.Integer(
            required=False,
            description='Maximum number of results to return',
            min=1,
            max=10000,
            example=100
        ),
        'offset': fields.Integer(
            required=False,
            description='Number of results to skip',
            min=0,
            example=0
        )
    })
    
    # Property shape query model
    property_shape_query_model = api.model('PropertyShapeQuery', {
        'node_shape': fields.String(
            required=True,
            description='URI of the node shape',
            example='http://ex.org/PersonShape'
        ),
        'limit': fields.Integer(
            required=False,
            description='Maximum number of results',
            example=100
        ),
        'offset': fields.Integer(
            required=False,
            description='Number of results to skip',
            example=0
        ),
        'shapes_graph_uri': fields.String(
            required=False,
            description='URI of the shapes graph',
            default='http://ex.org/ShapesGraph'
        ),
        'validation_report_uri': fields.String(
            required=False,
            description='URI of the validation report',
            default='http://ex.org/ValidationReport'
        )
    })
    
    return {
        'graph_uri': graph_uri_model,
        'shapes_graph': shapes_graph_model,
        'node_shape': node_shape_model,
        'pagination': pagination_model,
        'property_shape_query': property_shape_query_model
    }


# ==================== Response Models ====================

def create_response_models(api) -> Dict[str, Model]:
    """Create and register all response models with the API."""
    
    # Simple count response
    count_response_model = api.model('CountResponse', {
        'count': fields.Integer(
            required=True,
            description='The count value',
            example=42
        )
    })
    
    # Shapes count response (homepage)
    shapes_count_response_model = api.model('ShapesCountResponse', {
        'shapesCount': fields.Integer(
            required=True,
            description='Number of shapes in the graph',
            example=15
        )
    })
    
    # Violations count response
    violations_count_response_model = api.model('ViolationsCountResponse', {
        'violationsCount': fields.Integer(
            required=True,
            description='Number of violations in the validation report',
            example=127
        )
    })
    
    # Focus nodes count response
    focus_nodes_count_response_model = api.model('FocusNodesCountResponse', {
        'focusNodesCount': fields.Integer(
            required=True,
            description='Number of focus nodes in the validation report',
            example=38
        )
    })
    
    # URI list response
    uri_list_response_model = api.model('URIListResponse', {
        'uris': fields.List(
            fields.String,
            required=True,
            description='List of URIs',
            example=['http://ex.org/Shape1', 'http://ex.org/Shape2']
        ),
        'count': fields.Integer(
            required=True,
            description='Number of URIs in the list',
            example=2
        )
    })
    
    # Violation distribution item
    violation_distribution_item = api.model('ViolationDistributionItem', {
        'shape': fields.String(
            required=True,
            description='Shape URI',
            example='http://ex.org/PersonShape'
        ),
        'violationCount': fields.Integer(
            required=True,
            description='Number of violations for this shape',
            example=45
        )
    })
    
    # Violation distribution response
    violation_distribution_response_model = api.model('ViolationDistributionResponse', {
        'distributions': fields.List(
            fields.Nested(violation_distribution_item),
            required=True,
            description='List of violation distributions'
        )
    })
    
    # Property shape detail
    property_shape_detail = api.model('PropertyShapeDetail', {
        'propertyShape': fields.String(
            required=True,
            description='Property shape URI',
            example='http://ex.org/PersonShape/nameProperty'
        ),
        'violationsCount': fields.Integer(
            required=True,
            description='Number of violations',
            example=12
        ),
        'constraintsCount': fields.Integer(
            required=True,
            description='Number of constraints',
            example=3
        ),
        'mostViolatedConstraint': fields.String(
            required=False,
            description='Most violated constraint component',
            example='http://www.w3.org/ns/shacl#MinLengthConstraintComponent'
        )
    })
    
    # Property shapes list response
    property_shapes_response_model = api.model('PropertyShapesResponse', {
        'propertyShapes': fields.List(
            fields.Nested(property_shape_detail),
            required=True,
            description='List of property shapes with details'
        )
    })
    
    # Health check response
    health_response_model = api.model('HealthResponse', {
        'status': fields.String(
            required=True,
            description='Health status',
            enum=['healthy', 'unhealthy'],
            example='healthy'
        ),
        'version': fields.String(
            required=True,
            description='API version',
            example='1.0.0'
        ),
        'timestamp': fields.String(
            required=True,
            description='Current timestamp',
            example='2026-01-20T10:30:00Z'
        )
    })
    
    # Readiness check response
    readiness_response_model = api.model('ReadinessResponse', {
        'status': fields.String(
            required=True,
            description='Readiness status',
            enum=['ready', 'not ready'],
            example='ready'
        ),
        'checks': fields.Raw(
            required=True,
            description='Status of individual checks',
            example={'sparql_endpoint': 'ok', 'database': 'ok'}
        )
    })
    
    return {
        'count': count_response_model,
        'shapes_count': shapes_count_response_model,
        'violations_count': violations_count_response_model,
        'focus_nodes_count': focus_nodes_count_response_model,
        'uri_list': uri_list_response_model,
        'violation_distribution': violation_distribution_response_model,
        'property_shapes': property_shapes_response_model,
        'health': health_response_model,
        'readiness': readiness_response_model
    }


# ==================== Error Models ====================

def create_error_models(api) -> Dict[str, Model]:
    """Create and register all error models with the API."""
    
    # Error response model
    error_model = api.model('Error', {
        'error_code': fields.String(
            required=True,
            description='Error code for programmatic handling',
            example='VAL_INVALID_URI'
        ),
        'message': fields.String(
            required=True,
            description='Human-readable error message',
            example='The provided URI format is invalid'
        ),
        'details': fields.String(
            required=False,
            description='Additional error details',
            example='URI must start with http:// or https://'
        )
    })
    
    # Validation error model
    validation_error_model = api.model('ValidationError', {
        'error_code': fields.String(
            required=True,
            description='Validation error code',
            example='VAL_INVALID_PARAMETER',
            enum=[
                'VAL_INVALID_URI',
                'VAL_INVALID_PARAMETER',
                'VAL_MISSING_PARAMETER',
                'VAL_INVALID_FORMAT',
                'VAL_OUT_OF_RANGE'
            ]
        ),
        'message': fields.String(
            required=True,
            description='Error message',
            example='Parameter validation failed'
        ),
        'field': fields.String(
            required=False,
            description='Field that failed validation',
            example='graph_uri'
        )
    })
    
    # Query error model
    query_error_model = api.model('QueryError', {
        'error_code': fields.String(
            required=True,
            description='Query error code',
            example='QRY_EXECUTION_FAILED',
            enum=[
                'QRY_EXECUTION_FAILED',
                'QRY_TIMEOUT',
                'QRY_INVALID_SYNTAX',
                'QRY_CONNECTION_ERROR'
            ]
        ),
        'message': fields.String(
            required=True,
            description='Error message',
            example='SPARQL query execution failed'
        )
    })
    
    return {
        'error': error_model,
        'validation_error': validation_error_model,
        'query_error': query_error_model
    }


def register_all_models(api):
    """
    Register all API models with the Flask-RESTX API instance.
    
    Args:
        api: Flask-RESTX Api instance
        
    Returns:
        dict: Dictionary containing all registered models grouped by type
    """
    input_models = create_input_models(api)
    response_models = create_response_models(api)
    error_models = create_error_models(api)
    
    return {
        'input': input_models,
        'response': response_models,
        'error': error_models
    }
