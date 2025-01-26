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
)

shape_view_bp = Blueprint('shape_view', __name__)

# Route to get the number of violated focus nodes for a Node Shape
@shape_view_bp.route('/shape_view/violations/node-shape/focus-nodes/count', methods=['GET'])
def get_violated_focus_for_node_shape():
    try:
        node_shape = request.args.get("node_shape")
        if not node_shape:
            return jsonify({'error': 'node_shape is required'}), 400

        result = get_number_of_violated_focus_for_node_shape(node_shape)
        return jsonify({'nodeShape': node_shape, 'violatedFocusNodesCount': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# Route to get the number of property paths for a Node Shape
@shape_view_bp.route('/shape_view/node-shape/property-paths/count', methods=['GET'])
def get_property_paths_for_node_shape():
    try:
        node_shape = request.args.get("node_shape")
        if not node_shape:
            return jsonify({'error': 'node_shape is required'}), 400

        result = get_number_of_property_paths_for_node_shape(node_shape)
        return jsonify({'nodeShape': node_shape, 'propertyPathCount': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

# Route to get the number of constraints for a Node Shape
@shape_view_bp.route('/shape_view/node-shape/constraints/count', methods=['GET'])
def get_constraints_for_node_shape():
    try:
        node_shape = request.args.get("node_shape")
        if not node_shape:
            return jsonify({'error': 'node_shape is required'}), 400

        result = get_number_of_constraints_for_node_shape(node_shape)
        return jsonify({'nodeShape': node_shape, 'constraintCount': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# Route to get Property Shapes for a Node Shape
@shape_view_bp.route('/shape_view/node-shape/property-shapes', methods=['GET'])
def get_property_shapes_for_node_shape():
    try:
        node_shape = request.args.get("node_shape")
        limit = request.args.get("limit", type=int)
        offset = request.args.get("offset", type=int)

        if not node_shape:
            return jsonify({'error': 'node_shape is required'}), 400

        result = get_property_shapes(node_shape, limit=limit, offset=offset)
        return jsonify({'nodeShape': node_shape, 'propertyShapes': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# Route to get the number of violations for a specific Node Shape
@shape_view_bp.route('/shape_view/violations/node-shape/count', methods=['GET'])
def get_violations_for_node_shape():
    try:
        nodeshape_name = request.args.get("nodeshape_name")
        if not nodeshape_name:
            return jsonify({'error': 'nodeshape_name is required'}), 400

        result = get_number_of_violations_for_node_shape(nodeshape_name)
        return jsonify({'nodeShape': nodeshape_name, 'violationCount': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# Route to get the number of violations per constraint type for each Property Shape in a Node Shape
@shape_view_bp.route('/shape_view/violations/property-shapes/constraint-types', methods=['GET'])
def get_violations_per_constraint_type_for_property_shape():
    """
    Route to retrieve the number of violations per constraint type for each Property Shape 
    associated with a Node Shape.
    """
    try:
        node_shape = request.args.get("node_shape")
        if not node_shape:
            return jsonify({'error': 'node_shape is required'}), 400

        result = get_number_of_violations_per_constraint_type_for_property_shape(node_shape)
        return jsonify({'nodeShape': node_shape, 'propertyShapes': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get the total constraints count per Node Shape
@shape_view_bp.route('/shape_view/node-shapes/constraints/total-count', methods=['GET'])
def get_total_constraints_count_per_node_shape_route():
    """
    Route to retrieve the total constraints count for each Node Shape in the Shapes Graph.
    """
    try:
        result = get_total_constraints_count_per_node_shape()
        return jsonify({'totalConstraintsCountPerNodeShape': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get the constraints count for Property Shapes in a Node Shape
@shape_view_bp.route('/shape_view/property-shapes/constraints/count', methods=['GET'])
def get_constraints_count_for_property_shapes_route():
    """
    Route to retrieve the constraints count for each Property Shape in a specific Node Shape.
    """
    try:
        nodeshape_name = request.args.get("nodeshape_name")
        if not nodeshape_name:
            return jsonify({'error': 'nodeshape_name is required'}), 400

        result = get_constraints_count_for_property_shapes(nodeshape_name)
        return jsonify({'nodeShape': nodeshape_name, 'propertyShapesConstraints': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
