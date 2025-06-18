from flask import Blueprint, request, jsonify
from functions import (
    get_all_shapes_names,
    get_all_focus_node_names,
    get_all_property_path_names,
    get_all_constraint_components_names,
    get_violations_for_shape_name,
    # get_number_of_shapes_in_shapes_graph,
    get_number_of_node_shapes,
    get_number_of_node_shapes_with_violations,
    map_property_shapes_to_node_shapes,
    get_number_of_violations_for_node_shape,
    get_shape_from_shapes_graph,
    get_maximum_number_of_violations_in_validation_report_for_node_shape,
    get_average_number_of_violations_in_validation_report_for_node_shape,
    get_number_of_violated_focus_for_node_shape,
    get_number_of_property_paths_for_node_shape,
    get_number_of_constraints_for_node_shape,
    get_property_shapes,
    get_number_of_violations_per_constraint_type_for_property_shape,
    get_total_constraints_count_per_node_shape,
    get_constraints_count_for_property_shapes,
)

shapes_overview_bp = Blueprint('shapes_overview', __name__)

"""
Shapes Overview Routes Module

This module defines the API endpoints for analyzing and reporting on the overall
structure and content of the SHACL shapes graph and validation results. It provides
routes for retrieving shape names, statistics, and relationships in the validation schema.

Key Endpoint Groups:

- Entity Name Endpoints:
  - /shapes/names: Get all shape names
  - /focus-nodes/names: Get all focus node names
  - /property-paths/names: Get all property path names
  - /constraint-components/names: Get all constraint component names

- Statistics Endpoints:
  - /shapes/graph/count: Get number of shapes in shapes graph
  - /shapes/violations/count: Get count of shapes with violations
  - /violations/max: Get maximum number of violations for any shape
  - /violations/average: Get average number of violations across shapes

- Shape-Specific Endpoints:
  - /violations/shape: Get violations for a specific shape
  - /violations/node-shape/count: Get violation count for a node shape
  - /violations/node-shape/focus-nodes/count: Get count of violated focus nodes
  - /node-shape/property-paths/count: Get property path count for a node shape
  - /node-shape/constraints/count: Get constraint count for a node shape

- Property Shape Endpoints:
  - /property-to-node/map: Get mapping of property shapes to node shapes
  - /node-shape/property-shapes: Get property shapes for a node shape
  - /node-shape/property-shapes/violations: Get violations by constraint type

- Detailed Analysis Endpoints:
  - /shapes/graph/details: POST endpoint to get detailed shape information
  - /node-shape/constraints/total: Get total constraints count by node shape

All endpoints support customization through query parameters for graph URIs,
allowing flexibility in targeting different validation reports and shapes graphs.
"""


# Route to get all shapes names
@shapes_overview_bp.route('/shapes/names', methods=['GET'])
def get_shapes_names():
    try:
        graph_uri = request.args.get("graph_uri", default="http://ex.org/ValidationReport")
        result = get_all_shapes_names(graph_uri)
        return jsonify({'shapes': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get all focus node names
@shapes_overview_bp.route('/focus-nodes/names', methods=['GET'])
def get_focus_node_names():
    try:
        graph_uri = request.args.get("graph_uri", default="http://ex.org/ValidationReport")
        result = get_all_focus_node_names(graph_uri)
        return jsonify({'focusNodes': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get all property path names
@shapes_overview_bp.route('/property-paths/names', methods=['GET'])
def get_property_path_names():
    try:
        graph_uri = request.args.get("graph_uri", default="http://ex.org/ValidationReport")
        result = get_all_property_path_names(graph_uri)
        return jsonify({'propertyPaths': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get all constraint component names
@shapes_overview_bp.route('/constraint-components/names', methods=['GET'])
def get_constraint_components_names():
    try:
        graph_uri = request.args.get("graph_uri", default="http://ex.org/ValidationReport")
        result = get_all_constraint_components_names(graph_uri)
        return jsonify({'constraintComponents': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get violations for a shape name
@shapes_overview_bp.route('/violations/shape', methods=['GET'])
def get_violations_by_shape():
    try:
        shape_name = request.args.get("shape_name")
        graph_uri = request.args.get("graph_uri", default="http://ex.org/ValidationReport")
        if not shape_name:
            return jsonify({'error': 'shape_name is required'}), 400

        result = get_violations_for_shape_name(shape_name, graph_uri)
        return jsonify({'violations': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get the number of shapes in the shapes graph
@shapes_overview_bp.route('/shapes/graph/count', methods=['GET'])
def get_shapes_count_in_graph():
    try:
        graph_uri = request.args.get("graph_uri", default="http://ex.org/ShapesGraph")
        result = get_number_of_node_shapes(graph_uri)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get the number of node shapes with violations in the validation report
@shapes_overview_bp.route('/shapes/violations/count', methods=['GET'])
def get_node_shapes_with_violations_count():
    try:
        shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        
        # Call the function to calculate the number of node shapes with violations
        result = get_number_of_node_shapes_with_violations(shapes_graph_uri, validation_report_uri)
        
        return jsonify({'nodeShapesWithViolationsCount': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to map property shapes to node shapes
@shapes_overview_bp.route('/property-to-node/map', methods=['GET'])
def map_property_shapes():
    try:
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")
        result = map_property_shapes_to_node_shapes(validation_report_uri, shapes_graph_uri)
        return jsonify({'mapping': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get shape details from shapes graph
@shapes_overview_bp.route('/shapes/graph/details', methods=['POST'])
def get_shape_details():
    try:
        data = request.get_json()
        node_shape_names = data.get("node_shape_names")
        if not node_shape_names or not isinstance(node_shape_names, list):
            return jsonify({'error': 'node_shape_names must be a non-empty list'}), 400

        result = get_shape_from_shapes_graph(node_shape_names)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get the maximum number of violations for a node shape
@shapes_overview_bp.route('/violations/max', methods=['GET'])
def get_max_violations_for_node_shape():
    try:
        result = get_maximum_number_of_violations_in_validation_report_for_node_shape()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get the average number of violations for node shapes
@shapes_overview_bp.route('/violations/average', methods=['GET'])
def get_average_violations_for_node_shapes():
    try:
        result = get_average_number_of_violations_in_validation_report_for_node_shape()
        return jsonify({'averageViolations': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

# Route to get the number of violations for a specific Node Shape
@shapes_overview_bp.route('/violations/node-shape/count', methods=['GET'])
def get_violations_for_node_shape():
    try:
        nodeshape_name = request.args.get("nodeshape_name")
        if not nodeshape_name:
            return jsonify({'error': 'nodeshape_name is required'}), 400

        result = get_number_of_violations_for_node_shape(nodeshape_name)
        return jsonify({'nodeShape': nodeshape_name, 'violationCount': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to get the number of violated focus nodes for a Node Shape
@shapes_overview_bp.route('/violations/node-shape/focus-nodes/count', methods=['GET'])
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
@shapes_overview_bp.route('/node-shape/property-paths/count', methods=['GET'])
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
@shapes_overview_bp.route('/node-shape/constraints/count', methods=['GET'])
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
@shapes_overview_bp.route('/node-shape/property-shapes', methods=['GET'])
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


# Route to get violations per constraint type for Property Shapes of a Node Shape
@shapes_overview_bp.route('/node-shape/property-shapes/violations', methods=['GET'])
def get_violations_per_constraint_type():
    try:
        node_shape = request.args.get("node_shape")
        if not node_shape:
            return jsonify({'error': 'node_shape is required'}), 400

        result = get_number_of_violations_per_constraint_type_for_property_shape(node_shape)
        return jsonify({'nodeShape': node_shape, 'violationsPerConstraintType': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# Route to get total constraints count per Node Shape
@shapes_overview_bp.route('/node-shape/constraints/total', methods=['GET'])
def get_total_constraints_count():
    try:
        # Get the shapes graph URI from the request arguments, or use the default value
        shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")

        # Call the function to get the constraints count per Node Shape
        result = get_total_constraints_count_per_node_shape(shapes_graph_uri)
        return jsonify({'shapesGraph': shapes_graph_uri, 'constraintsPerNodeShape': result}), 200

    except Exception as e:
        # Handle exceptions and return error response
        return jsonify({'error': str(e)}), 400
