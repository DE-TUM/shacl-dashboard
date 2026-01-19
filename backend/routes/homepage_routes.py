from flask import Blueprint, request, jsonify, Response
from typing import Tuple, Union
from error_handlers import handle_api_errors, validate_uri, validate_positive_integer
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
    generate_validation_details_report,
    get_most_violated_path,
    get_most_violated_node_shape,
    get_most_violated_focus_node,
    get_most_frequent_constraint_component,
    get_distinct_constraint_components_count,
    get_distinct_constraints_count_in_shapes,
    get_distribution_of_violations_per_constraint_component,
    
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
@handle_api_errors
def get_violations_count_in_report() -> Response:
    """
    Count the total number of violations in the validation report.
    
    Query Parameters:
        graph_uri (str, optional): The URI of the validation report graph.
            Defaults to "http://ex.org/ValidationReport".
    
    Returns:
        Response: JSON response containing the violation count.
            Format: {'violationCount': int}
    
    Raises:
        ValidationError: If the graph_uri parameter is invalid.
    """
    graph_uri = request.args.get("graph_uri", default="http://ex.org/ValidationReport")
    graph_uri = validate_uri(graph_uri, "graph_uri")
    result = get_number_of_violations_in_validation_report(graph_uri)
    return jsonify({'violationCount': result})

# Route to get the number of shapes in the shapes graph (node shape and property shape)
@homepage_bp.route('/homepage/shapes/graph/count', methods=['GET'])
@handle_api_errors
def get_shapes_count_in_graph() -> Response:
    """
    Count the total number of node shapes in the shapes graph.
    
    Query Parameters:
        graph_uri (str, optional): The URI of the shapes graph.
            Defaults to "http://ex.org/ShapesGraph".
    
    Returns:
        Response: JSON response containing the node shape count.
    
    Raises:
        ValidationError: If the graph_uri parameter is invalid.
    """
    graph_uri = request.args.get("graph_uri", default="http://ex.org/ShapesGraph")
    graph_uri = validate_uri(graph_uri, "graph_uri")
    result = get_number_of_node_shapes(graph_uri)
    return jsonify(result)
    
# Route to get the number of node shapes with violations in the validation report
@homepage_bp.route('/homepage/shapes/violations/count', methods=['GET'])
@handle_api_errors
def get_node_shapes_with_violations_count() -> Response:
    """
    Count the number of node shapes that have at least one violation.
    
    Query Parameters:
        shapes_graph_uri (str, optional): The URI of the shapes graph.
            Defaults to "http://ex.org/ShapesGraph".
        validation_report_uri (str, optional): The URI of the validation report graph.
            Defaults to "http://ex.org/ValidationReport".
    
    Returns:
        Response: JSON response containing the count of node shapes with violations.
            Format: {'nodeShapesWithViolationsCount': int}
    
    Raises:
        ValidationError: If any URI parameter is invalid.
    """
    shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")
    validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
    shapes_graph_uri = validate_uri(shapes_graph_uri, "shapes_graph_uri")
    validation_report_uri = validate_uri(validation_report_uri, "validation_report_uri")
    
    # Call the function to calculate the number of node shapes with violations
    result = get_number_of_node_shapes_with_violations(shapes_graph_uri, validation_report_uri)
    
    return jsonify({'nodeShapesWithViolationsCount': result})
    
# Route to get the number of unique paths in the shapes graph
@homepage_bp.route('/homepage/shapes/graph/paths/count', methods=['GET'])
@handle_api_errors
def get_paths_count_in_graph() -> Response:
    """
    Count the number of unique property paths in the shapes graph.
    
    Query Parameters:
        graph_uri (str, optional): The URI of the shapes graph.
            Defaults to "http://ex.org/ShapesGraph".
    
    Returns:
        Response: JSON response containing the unique path count.
            Format: {'uniquePathsCount': int}
    
    Raises:
        ValidationError: If the graph_uri parameter is invalid.
    """
    graph_uri = request.args.get("graph_uri", default="http://ex.org/ShapesGraph")
    graph_uri = validate_uri(graph_uri, "graph_uri")
    result = get_number_of_paths_in_shapes_graph(graph_uri)
    return jsonify({'uniquePathsCount': result})

# Route to get the number of unique paths with violations in the validation report
@homepage_bp.route('/homepage/validation-report/paths/violations/count', methods=['GET'])
@handle_api_errors
def get_paths_with_violations_count() -> Response:
    """
    Count the number of unique property paths that have violations.
    
    Query Parameters:
        validation_report_uri (str, optional): The URI of the validation report graph.
            Defaults to "http://ex.org/ValidationReport".
    
    Returns:
        Response: JSON response containing the count of paths with violations.
            Format: {'pathsWithViolationsCount': int}
    
    Raises:
        ValidationError: If the validation_report_uri parameter is invalid.
    """
    validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
    validation_report_uri = validate_uri(validation_report_uri, "validation_report_uri")
    result = get_number_of_paths_with_violations(validation_report_uri)
    return jsonify({'pathsWithViolationsCount': result})

# Route to get the number of unique focus nodes in the validation report
@homepage_bp.route('/homepage/validation-report/focus-nodes/count', methods=['GET'])
@handle_api_errors
def get_focus_nodes_count_in_report() -> Response:
    """
    Count the number of unique focus nodes in the validation report.
    
    Query Parameters:
        validation_report_uri (str, optional): The URI of the validation report graph.
            Defaults to "http://ex.org/ValidationReport".
    
    Returns:
        Response: JSON response containing the focus node count.
            Format: {'focusNodesCount': int}
    
    Raises:
        ValidationError: If the validation_report_uri parameter is invalid.
    """
    validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
    validation_report_uri = validate_uri(validation_report_uri, "validation_report_uri")
    result = get_number_of_focus_nodes_in_validation_report(validation_report_uri)
    return jsonify({'focusNodesCount': result})

# Route to get violations per node shape
@homepage_bp.route('/homepage/shapes/violations', methods=['GET'])
@handle_api_errors
def get_violations_by_node_shape() -> Response:
    """
    Retrieve the number of violations for each node shape.
    
    Query Parameters:
        shapes_graph_uri (str, optional): The URI of the shapes graph.
            Defaults to "http://ex.org/ShapesGraph".
        validation_report_uri (str, optional): The URI of the validation report graph.
            Defaults to "http://ex.org/ValidationReport".
    
    Returns:
        Response: JSON response containing violations per node shape.
            Format: {'violationsPerNodeShape': [{'NodeShapeName': str, 'NumViolations': int}, ...]}
    
    Raises:
        ValidationError: If any URI parameter is invalid.
    """
    shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")
    validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
    shapes_graph_uri = validate_uri(shapes_graph_uri, "shapes_graph_uri")
    validation_report_uri = validate_uri(validation_report_uri, "validation_report_uri")
    result = get_violations_per_node_shape(shapes_graph_uri, validation_report_uri)
    return jsonify({'violationsPerNodeShape': result})

# Route to get violations per path
@homepage_bp.route('/homepage/validation-report/paths/violations', methods=['GET'])
@handle_api_errors
def get_violations_by_path() -> Response:
    """
    Retrieve the number of violations for each property path.
    
    Query Parameters:
        validation_report_uri (str, optional): The URI of the validation report graph.
            Defaults to "http://ex.org/ValidationReport".
    
    Returns:
        Response: JSON response containing violations per path.
            Format: {'violationsPerPath': [{'PathName': str, 'NumViolations': int}, ...]}
    
    Raises:
        ValidationError: If the validation_report_uri parameter is invalid.
    """
    validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
    validation_report_uri = validate_uri(validation_report_uri, "validation_report_uri")
    result = get_violations_per_path(validation_report_uri)
    return jsonify({'violationsPerPath': result})

# Route to get violations per focus node
@homepage_bp.route('/homepage/validation-report/focus-nodes/violations', methods=['GET'])
@handle_api_errors
def get_violations_by_focus_node() -> Response:
    """
    Retrieve the number of violations for each focus node.
    
    Query Parameters:
        validation_report_uri (str, optional): The URI of the validation report graph.
            Defaults to "http://ex.org/ValidationReport".
    
    Returns:
        Response: JSON response containing violations per focus node.
            Format: {'violationsPerFocusNode': [{'FocusNodeName': str, 'NumViolations': int}, ...]}
    
    Raises:
        ValidationError: If the validation_report_uri parameter is invalid.
    """
    validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
    validation_report_uri = validate_uri(validation_report_uri, "validation_report_uri")
    result = get_violations_per_focus_node(validation_report_uri)
    return jsonify({'violationsPerFocusNode': result})


# Route to get distribution of violations per node shape
@homepage_bp.route('/homepage/violations/distribution/shape', methods=['GET'])
@handle_api_errors
def get_distribution_of_violations_per_shape() -> Tuple[Response, int]:
    """
    API to get the distribution of violations per node shape.
    """
    shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")
    validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
    shapes_graph_uri = validate_uri(shapes_graph_uri, "shapes_graph_uri")
    validation_report_uri = validate_uri(validation_report_uri, "validation_report_uri")
    result = distribution_of_violations_per_shape(shapes_graph_uri, validation_report_uri)
    return jsonify(result), 200


# Route to get distribution of violations per path
@homepage_bp.route('/homepage/violations/distribution/path', methods=['GET'])
@handle_api_errors
def get_distribution_of_violations_per_path() -> Tuple[Response, int]:
    """
    API to get the distribution of violations per path.
    """
    validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
    validation_report_uri = validate_uri(validation_report_uri, "validation_report_uri")
    result = distribution_of_violations_per_path(validation_report_uri)
    return jsonify(result), 200


# Route to get distribution of violations per focus node
@homepage_bp.route('/homepage/violations/distribution/focus-node', methods=['GET'])
@handle_api_errors
def get_distribution_of_violations_per_focus_node() -> Tuple[Response, int]:
    """
    API to get the distribution of violations per focus node.
    """
    validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
    validation_report_uri = validate_uri(validation_report_uri, "validation_report_uri")
    result = distribution_of_violations_per_focus_node(validation_report_uri)
    return jsonify(result), 200


@homepage_bp.route('/homepage/validation-details', methods=['GET'])
@handle_api_errors
def get_validation_details_report() -> Tuple[Response, int]:
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
    # Get query parameters with default values
    validation_report_uri = request.args.get("validation_report_uri", default="http://ex.org/ValidationReport")
    shapes_graph_uri = request.args.get("shapes_graph_uri", default="http://ex.org/ShapesGraph")
    limit = validate_positive_integer(request.args.get("limit", 10), "limit")
    offset = validate_positive_integer(request.args.get("offset", 0), "offset")
    
    validation_report_uri = validate_uri(validation_report_uri, "validation_report_uri")
    shapes_graph_uri = validate_uri(shapes_graph_uri, "shapes_graph_uri")

    # Call the generate_validation_details_report function
    report = generate_validation_details_report(
        validation_report_uri=validation_report_uri,
        shapes_graph_uri=shapes_graph_uri,
        limit=limit,
        offset=offset
    )

    # Return the report as JSON
    return jsonify(report), 200

# Route to get the number of node shapes in the shapes graph
@homepage_bp.route('/homepage/nodeshapes/count', methods=['GET'])
@handle_api_errors
def get_number_of_node_shapes_route() -> Response:
    """
    Count the total number of node shapes in the default shapes graph.
    
    Returns:
        Response: JSON response containing the node shape count.
            Format: {'nodeShapeCount': int}
    
    Raises:
        RuntimeError: If the SPARQL query fails.
    """
    result = get_number_of_node_shapes()
    return jsonify({'nodeShapeCount': result})


# Route to get the most violated node shape
@homepage_bp.route('/homepage/violations/most-violated-node-shape', methods=['GET'])
@handle_api_errors
def get_most_violated_node_shape_route() -> Response:
    """
    Find the node shape with the highest number of violations.
    
    Returns:
        Response: JSON response containing the most violated node shape.
            Format: {'nodeShape': str, 'violations': int}
    
    Raises:
        RuntimeError: If the SPARQL query fails.
    """
    result = get_most_violated_node_shape()
    return jsonify(result)


# Route to get the most violated path
@homepage_bp.route('/homepage/violations/most-violated-path', methods=['GET'])
@handle_api_errors
def get_most_violated_path_route() -> Response:
    """
    Find the property path with the highest number of violations.
    
    Returns:
        Response: JSON response containing the most violated path.
            Format: {'path': str, 'violations': int}
    
    Raises:
        RuntimeError: If the SPARQL query fails.
    """
    result = get_most_violated_path()
    return jsonify(result)


# Route to get the most violated focus node
@homepage_bp.route('/homepage/violations/most-violated-focus-node', methods=['GET'])
@handle_api_errors
def get_most_violated_focus_node_route() -> Response:
    """
    Find the focus node with the highest number of violations.
    
    Returns:
        Response: JSON response containing the most violated focus node.
            Format: {'focusNode': str, 'violations': int}
    
    Raises:
        RuntimeError: If the SPARQL query fails.
    """
    result = get_most_violated_focus_node()
    return jsonify(result)


# Route to get the most frequent constraint component
@homepage_bp.route('/homepage/violations/most-frequent-constraint-component', methods=['GET'])
@handle_api_errors
def get_most_frequent_constraint_component_route() -> Response:
    """
    Find the constraint component that appears most frequently in violations.
    
    Returns:
        Response: JSON response containing the most frequent constraint component.
            Format: {'constraintComponent': str, 'occurrences': int}
    
    Raises:
        RuntimeError: If the SPARQL query fails.
    """
    result = get_most_frequent_constraint_component()
    return jsonify(result)


# Route to get the count of distinct constraint components in the validation report
@homepage_bp.route('/homepage/violations/distinct-constraint-components/count', methods=['GET'])
@handle_api_errors
def get_distinct_constraint_components_count_route() -> Response:
    """
    Count the number of distinct constraint components in violations.
    
    Returns:
        Response: JSON response containing the distinct constraint component count.
            Format: {'distinctConstraintComponentCount': int}
    
    Raises:
        RuntimeError: If the SPARQL query fails.
    """
    result = get_distinct_constraint_components_count()
    return jsonify({'distinctConstraintComponentCount': result})


# Route to get the count of distinct constraints in the shapes graph
@homepage_bp.route('/homepage/shapes/distinct-constraints/count', methods=['GET'])
@handle_api_errors
def get_distinct_constraints_count_in_shapes_route() -> Response:
    """
    Count the number of distinct constraint types used in the shapes graph.
    
    Returns:
        Response: JSON response containing the distinct constraints count.
            Format: {'distinctConstraintsCount': int}
    
    Raises:
        RuntimeError: If the SPARQL query fails.
    """
    result = get_distinct_constraints_count_in_shapes()
    return jsonify({'distinctConstraintsCount': result})


# Route to get the distribution of violations per constraint component
@homepage_bp.route('/homepage/violations/distribution-per-constraint-component', methods=['GET'])
@handle_api_errors
def get_distribution_of_violations_per_constraint_component_route() -> Response:
    """
    Generate distribution data for violations grouped by constraint component.
    
    Returns:
        Response: JSON response containing bar chart data with labels and datasets.
            Format: {'labels': [str, ...], 'datasets': [{'label': str, 'data': [int, ...]}]}
    
    Raises:
        RuntimeError: If the SPARQL query fails.
    """
    result = get_distribution_of_violations_per_constraint_component()
    return jsonify(result)
