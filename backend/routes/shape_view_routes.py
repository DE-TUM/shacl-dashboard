from flask import Blueprint, request, jsonify
from functions import (
    get_number_of_violations_for_node_shape,
    get_number_of_violated_focus_for_node_shape,
    get_number_of_property_paths_for_node_shape,
    get_number_of_constraints_for_node_shape,
    get_property_shapes,
    get_number_of_violations_per_constraint_type_for_property_shape,
    get_total_constraints_count_per_node_shape,
    get_constraints_count_for_property_shapes,
    get_node_shape_with_violations,
)
from error_handlers import handle_api_errors, validate_uri, validate_positive_integer, ValidationError

"""
Shape View Routes Module

This module defines the API endpoints for detailed inspection and analysis of
individual SHACL shapes. It provides routes for retrieving detailed information
about specific node shapes, their property shapes, constraints, and associated
validation results.

Key Endpoints:
- /shape_view/violations/node-shape/count: Get violation count for a node shape
  - Query param: nodeshape_name (required)

- /shape_view/violations/node-shape/focus-nodes/count: Get count of violated focus nodes
  - Query param: node_shape (required)

- /shape_view/node-shape/property-paths/count: Get property path count for a node shape
  - Query param: node_shape (required)

- /shape_view/node-shape/constraints/count: Get constraint count for a node shape
  - Query param: node_shape (required)

- /shape_view/node-shape/property-shapes: Get property shapes for a node shape
  - Query params: node_shape (required), limit (optional), offset (optional)

All endpoints return detailed information about the requested shape aspects,
enabling focused analysis of specific shapes and their validation issues.
"""

shape_view_bp = Blueprint('shape_view', __name__)

# Route to get the number of violated focus nodes for a Node Shape
@shape_view_bp.route('/shape_view/violations/node-shape/focus-nodes/count', methods=['GET'])
@handle_api_errors
def get_violated_focus_for_node_shape():
    node_shape = request.args.get("node_shape")
    if not node_shape:
        raise ValidationError('node_shape is required')
    
    node_shape = validate_uri(node_shape, "node_shape")
    result = get_number_of_violated_focus_for_node_shape(node_shape)
    return jsonify({'nodeShape': node_shape, 'violatedFocusNodesCount': result}), 200
    
# Route to get the number of property paths for a Node Shape
@shape_view_bp.route('/shape_view/node-shape/property-paths/count', methods=['GET'])
@handle_api_errors
def get_property_paths_for_node_shape():
    node_shape = request.args.get("node_shape")
    if not node_shape:
        raise ValidationError('node_shape is required')
    
    node_shape = validate_uri(node_shape, "node_shape")
    result = get_number_of_property_paths_for_node_shape(node_shape)
    return jsonify({'nodeShape': node_shape, 'propertyPathCount': result}), 200
    

# Route to get the number of constraints for a Node Shape
@shape_view_bp.route('/shape_view/node-shape/constraints/count', methods=['GET'])
@handle_api_errors
def get_constraints_for_node_shape():
    node_shape = request.args.get("node_shape")
    if not node_shape:
        raise ValidationError('node_shape is required')
    
    node_shape = validate_uri(node_shape, "node_shape")
    result = get_number_of_constraints_for_node_shape(node_shape)
    return jsonify({'nodeShape': node_shape, 'constraintCount': result}), 200
    
# Route to get Property Shapes for a Node Shape
@shape_view_bp.route('/shape_view/node-shape/property-shapes', methods=['GET'])
@handle_api_errors
def get_property_shapes_for_node_shape():
    node_shape = request.args.get("node_shape")
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", type=int)

    if not node_shape:
        raise ValidationError('node_shape is required')
    
    node_shape = validate_uri(node_shape, "node_shape")
    if limit is not None:
        limit = validate_positive_integer(limit, "limit")
    if offset is not None:
        offset = validate_positive_integer(offset, "offset")

    result = get_property_shapes(node_shape, limit=limit, offset=offset)
    return jsonify({'nodeShape': node_shape, 'propertyShapes': result}), 200
    
# Route to get the number of violations for a specific Node Shape
@shape_view_bp.route('/shape_view/violations/node-shape/count', methods=['GET'])
@handle_api_errors
def get_violations_for_node_shape():
    nodeshape_name = request.args.get("nodeshape_name")
    if not nodeshape_name:
        raise ValidationError('nodeshape_name is required')
    
    nodeshape_name = validate_uri(nodeshape_name, "nodeshape_name")
    result = get_number_of_violations_for_node_shape(nodeshape_name)
    return jsonify({'nodeShape': nodeshape_name, 'violationCount': result}), 200
    
# Route to get the number of violations per constraint type for each Property Shape in a Node Shape
@shape_view_bp.route('/shape_view/violations/property-shapes/constraint-types', methods=['GET'])
@handle_api_errors
def get_violations_per_constraint_type_for_property_shape():
    """
    Route to retrieve the number of violations per constraint type for each Property Shape 
    associated with a Node Shape.
    """
    node_shape = request.args.get("node_shape")
    if not node_shape:
        raise ValidationError('node_shape is required')
    
    node_shape = validate_uri(node_shape, "node_shape")
    result = get_number_of_violations_per_constraint_type_for_property_shape(node_shape)
    return jsonify({'nodeShape': node_shape, 'propertyShapes': result}), 200


# Route to get the total constraints count per Node Shape
@shape_view_bp.route('/shape_view/node-shapes/constraints/total-count', methods=['GET'])
@handle_api_errors
def get_total_constraints_count_per_node_shape_route():
    """
    Route to retrieve the total constraints count for each Node Shape in the Shapes Graph.
    """
    result = get_total_constraints_count_per_node_shape()
    return jsonify({'totalConstraintsCountPerNodeShape': result}), 200


# Route to get the constraints count for Property Shapes in a Node Shape
@shape_view_bp.route('/shape_view/property-shapes/constraints/count', methods=['GET'])
@handle_api_errors
def get_constraints_count_for_property_shapes_route():
    """
    Route to retrieve the constraints count for each Property Shape in a specific Node Shape.
    """
    nodeshape_name = request.args.get("nodeshape_name")
    if not nodeshape_name:
        raise ValidationError('nodeshape_name is required')
    
    nodeshape_name = validate_uri(nodeshape_name, "nodeshape_name")
    result = get_constraints_count_for_property_shapes(nodeshape_name)
    return jsonify({'nodeShape': nodeshape_name, 'propertyShapesConstraints': result}), 200


# Route to get node shape with all property shapes and their detailed violations
@shape_view_bp.route('/shape_view/node-shape/violations-detailed', methods=['GET'])
@handle_api_errors
def get_node_shape_violations_detailed():
    """
    Get node shape with all property shapes and their detailed violations.
    Returns comprehensive violation details including focus nodes, result paths, messages, etc.
    """
    node_shape = request.args.get("node_shape")
    limit_violations = request.args.get("limit_violations", type=int)
    offset_violations = request.args.get("offset_violations", type=int)

    if not node_shape:
        raise ValidationError('node_shape is required')
    
    node_shape = validate_uri(node_shape, "node_shape")
    if limit_violations is not None:
        limit_violations = validate_positive_integer(limit_violations, "limit_violations")
    if offset_violations is not None:
        offset_violations = validate_positive_integer(offset_violations, "offset_violations")

    result = get_node_shape_with_violations(
        node_shape,
        limit_violations_per_property=limit_violations,
        offset_violations_per_property=offset_violations
    )
    return jsonify(result), 200
