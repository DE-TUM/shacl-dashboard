from flask import Blueprint, request, jsonify
from functions import (
    get_number_of_node_shapes,
    get_number_of_node_shapes_with_violations,
    get_number_of_paths_in_shapes_graph,
    get_number_of_paths_with_violations,
    get_number_of_focus_nodes_in_validation_report,
    get_violations_per_node_shape,
    get_violations_per_path,
    get_violations_per_focus_node,
    get_number_of_violations_in_validation_report,
    distribution_of_violations_per_shape,
    distribution_of_violations_per_path,
    distribution_of_violations_per_focus_node,
    generate_validation_details_report
)

"""
Homepage Routes Module

This module defines the API endpoints related to the main dashboard functionality
of the SHACL Dashboard application. It provides routes for retrieving statistics,
distributions, and detailed reports about SHACL validation results.

Route groups:
- Counts and statistics (/homepage/*count)
- Violation distributions (/homepage/violations/distribution/*)
- Detailed validation reports (/homepage/validation-details)
- Entity-specific violations (/homepage/*/violations)
"""


homepage_bp = Blueprint('homepage', __name__)

# Route to get the number of violations in the validation report
@homepage_bp.route('/homepage/violations/report/count', methods=['GET'])
def get_violations_count_in_report():
    try:
        graph_uri = request.args.get("graph_uri", default="http://ex.org/ValidationReport")
        result = get_number_of_violations_in_validation_report(graph_uri)
        return jsonify({'violationCount': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to get the number of shapes in the shapes graph (node shape and property shape)
@homepage_bp.route('/homepage/shapes/graph/count', methods=['GET'])
def get_shapes_count_in_graph():
    try:
        graph_uri = request.args.get("graph_uri", default="http://ex.org/ShapesGraph")
        result = get_number_of_node_shapes(graph_uri)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# Route to get the number of node shapes with violations in the validation report
@homepage_bp.route('/homepage/shapes/violations/count', methods=['GET'])
def get_node_shapes_with_violations_count():
    try:
        shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        
        # Call the function to calculate the number of node shapes with violations
        result = get_number_of_node_shapes_with_violations(shapes_graph_uri, validation_report_uri)
        
        return jsonify({'nodeShapesWithViolationsCount': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# Route to get the number of unique paths in the shapes graph
@homepage_bp.route('/homepage/shapes/graph/paths/count', methods=['GET'])
def get_paths_count_in_graph():
    try:
        graph_uri = request.args.get("graph_uri", default="http://ex.org/ShapesGraph")
        result = get_number_of_paths_in_shapes_graph(graph_uri)
        return jsonify({'uniquePathsCount': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to get the number of unique paths with violations in the validation report
@homepage_bp.route('/homepage/validation-report/paths/violations/count', methods=['GET'])
def get_paths_with_violations_count():
    try:
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        result = get_number_of_paths_with_violations(validation_report_uri)
        return jsonify({'pathsWithViolationsCount': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to get the number of unique focus nodes in the validation report
@homepage_bp.route('/homepage/validation-report/focus-nodes/count', methods=['GET'])
def get_focus_nodes_count_in_report():
    try:
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        result = get_number_of_focus_nodes_in_validation_report(validation_report_uri)
        return jsonify({'focusNodesCount': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to get violations per node shape
@homepage_bp.route('/homepage/shapes/violations', methods=['GET'])
def get_violations_by_node_shape():
    try:
        shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        result = get_violations_per_node_shape(shapes_graph_uri, validation_report_uri)
        return jsonify({'violationsPerNodeShape': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to get violations per path
@homepage_bp.route('/homepage/validation-report/paths/violations', methods=['GET'])
def get_violations_by_path():
    try:
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        result = get_violations_per_path(validation_report_uri)
        return jsonify({'violationsPerPath': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to get violations per focus node
@homepage_bp.route('/homepage/validation-report/focus-nodes/violations', methods=['GET'])
def get_violations_by_focus_node():
    try:
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        result = get_violations_per_focus_node(validation_report_uri)
        return jsonify({'violationsPerFocusNode': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get distribution of violations per node shape
@homepage_bp.route('/homepage/violations/distribution/shape', methods=['GET'])
def get_distribution_of_violations_per_shape():
    """
    API to get the distribution of violations per node shape.
    """
    try:
        shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        result = distribution_of_violations_per_shape(shapes_graph_uri, validation_report_uri)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get distribution of violations per path
@homepage_bp.route('/homepage/violations/distribution/path', methods=['GET'])
def get_distribution_of_violations_per_path():
    """
    API to get the distribution of violations per path.
    """
    try:
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        result = distribution_of_violations_per_path(validation_report_uri)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Route to get distribution of violations per focus node
@homepage_bp.route('/homepage/violations/distribution/focus-node', methods=['GET'])
def get_distribution_of_violations_per_focus_node():
    """
    API to get the distribution of violations per focus node.
    """
    try:
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        result = distribution_of_violations_per_focus_node(validation_report_uri)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@homepage_bp.route('/homepage/validation-details', methods=['GET'])
def get_validation_details_report():
    """
    API endpoint to generate a detailed validation report.

    Query Parameters:
        validation_report_uri (str): The URI of the Validation Report to query (optional, default is set in the function).
        shapes_graph_uri (str): The URI of the Shapes Graph to query (optional, default is set in the function).
        limit (int): Maximum number of violations to return (optional, default is 10).
        offset (int): Offset for the violations to return (optional, default is 0).

    Returns:
        JSON: A detailed validation report including prefixes, violations, and shape details.
    """
    try:
        # Get query parameters with default values
        validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
        shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))

        # Call the generate_validation_details_report function
        report = generate_validation_details_report(
            validation_report_uri=validation_report_uri,
            shapes_graph_uri=shapes_graph_uri,
            limit=limit,
            offset=offset
        )

        # Return the report as JSON
        return jsonify(report), 200

    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({'error': str(e)}), 400

