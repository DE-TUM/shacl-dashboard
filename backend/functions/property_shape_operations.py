import sys
import os
from typing import List, Dict, Optional, Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SHAPES_GRAPH_URI, VALIDATION_REPORT_URI, SHACL_FEATURES
from sparql_executor import SparqlQueryExecutor, get_default_executor
import logging

logger = logging.getLogger(__name__)

"""
Property Shape Operations Module

This module provides functions for working with property shapes, including
retrieving property shapes, analyzing violations per constraint type,
and getting detailed violation information.

Key functions:
- get_property_shapes: Get property shapes for a specific node shape
- get_number_of_violations_per_constraint_type_for_property_shape: Get violations per constraint type
- get_property_shape_with_violations: Get detailed violation information for a property shape
- get_node_shape_with_violations: Get detailed information for a node shape with all violations
- get_total_constraints_count_per_node_shape: Calculate total constraints per node shape
- get_constraints_count_for_property_shapes: Calculate constraints count for property shapes
"""


def get_property_shapes(node_shape: str, limit: Optional[int] = None, offset: Optional[int] = None, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI, executor: Optional[SparqlQueryExecutor] = None) -> List[Dict[str, Any]]:
    """
    Retrieve Property Shapes associated with the given Node Shape, including statistics about violations,
    constraints, and the most violated constraint.

    Args:
        node_shape (str): The URI of the Node Shape to query.
        limit (int, optional): Maximum number of Property Shapes to return. Default is None (no limit).
        offset (int, optional): Offset for the Property Shapes to return. Default is None (no offset).
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".
        executor (Optional[SparqlQueryExecutor]): Optional executor instance.

    Returns:
        list: A JSON list of Property Shapes with their statistics.
    """
    if executor is None:
        executor = get_default_executor()
    
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape

    # Build the SPARQL query with optional LIMIT and OFFSET
    query = f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """
    if limit is not None:
        query += f" LIMIT {limit}"
    if offset is not None:
        query += f" OFFSET {offset}"

    try:
        shapes_results = executor.execute_query(query, shapes_graph_uri, "get_property_shapes")
    except Exception as e:
        raise RuntimeError(f"Error querying Shapes Graph: {str(e)}")

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return an empty list
    if not property_shapes:
        return []

    # Initialize list to store the final result
    property_shapes_info = []

    # Step 2: For each Property Shape, calculate statistics
    for property_shape in property_shapes:
        # Query the number of violations for the Property Shape
        num_violations = executor.execute_count_query(
            f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{validation_report_uri}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> .
            }}
            """,
            validation_report_uri,
            "count_violations_for_property_shape",
            "violationCount"
        )

        if num_violations == 0:
            # If no violations, append default values and skip further checks
            property_shapes_info.append({
                "PropertyShapeName": property_shape,
                "NumViolations": 0,
                "NumConstraints": 0,
                "MostViolatedConstraint": None,
            })
        else:
            # Query the number of unique constraints for the Property Shape
            num_constraints = executor.execute_count_query(
                f"""
                SELECT (COUNT(DISTINCT ?constraintComponent) AS ?constraintCount)
                FROM <{validation_report_uri}>
                WHERE {{
                    ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                            <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
                }}
                """,
                validation_report_uri,
                "count_constraints_for_property_shape",
                "constraintCount"
            )

            # Query the most violated constraint for the Property Shape
            query = f"""
                SELECT ?constraintComponent (COUNT(?violation) AS ?violationCount)
                FROM <{validation_report_uri}>
                WHERE {{
                    ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                            <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
                }}
                GROUP BY ?constraintComponent
                ORDER BY DESC(?violationCount)
                LIMIT 1
            """
            most_violated_results = executor.execute_query(query, validation_report_uri, "find_most_violated_constraint")
            most_violated_constraint = (
                most_violated_results["results"]["bindings"][0]["constraintComponent"]["value"]
                if most_violated_results["results"]["bindings"] else None
            )

            # Append statistics for the current Property Shape
            property_shapes_info.append({
                "PropertyShapeName": property_shape,
                "NumViolations": num_violations,
                "NumConstraints": num_constraints,
                "MostViolatedConstraint": most_violated_constraint,
            })

    return property_shapes_info


def get_number_of_violations_per_constraint_type_for_property_shape(
    node_shape: str,
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> list:
    """
    Retrieve the number of violations per constraint type (sh:sourceConstraintComponent) for each
    Property Shape associated with the given Node Shape. Property Shapes with no violations are excluded.

    Args:
        node_shape (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".
        executor (Optional[SparqlQueryExecutor]): Optional executor instance.

    Returns:
        list: A JSON list of Property Shapes with their violations categorized by constraints.
    """
    if executor is None:
        executor = get_default_executor()
    
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    query = f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """

    try:
        shapes_results = executor.execute_query(query, shapes_graph_uri, "get_property_shapes")
    except Exception as e:
        raise RuntimeError(f"Error querying Shapes Graph: {str(e)}")

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return an empty list
    if not property_shapes:
        return []

    # Initialize list to store the final result
    property_shapes_info = []

    # Step 2: For each Property Shape, retrieve violations per constraint type
    for property_shape in property_shapes:
        # Query violations grouped by constraint type for the Property Shape
        query = f"""
            SELECT ?constraintComponent (COUNT(?violation) AS ?violationCount)
            FROM <{validation_report_uri}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                           <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
            }}
            GROUP BY ?constraintComponent
        """

        try:
            violations_results = executor.execute_query(query, validation_report_uri, "get_violations_per_constraint_type")
        except Exception as e:
            raise RuntimeError(f"Error querying Validation Report: {str(e)}")

        # Build the list of constraints and their violation counts
        constraints_info = [
            {
                "Constraint": result["constraintComponent"]["value"],
                "Violations": int(result["violationCount"]["value"])
            }
            for result in violations_results["results"]["bindings"]
        ]

        # Only include Property Shapes with non-empty Constraints
        if constraints_info:
            property_shapes_info.append({
                "PropertyShape": property_shape,
                "Constraints": constraints_info
            })

    return property_shapes_info


def get_property_shape_with_violations(
    property_shape: str,
    validation_report_uri: str = VALIDATION_REPORT_URI,
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    limit: int = None,
    offset: int = None,
    executor: Optional[SparqlQueryExecutor] = None
) -> Dict[str, Any]:
    """
    Get detailed violation information for a single property shape.
    
    Args:
        property_shape (str): The URI of the Property Shape to query.
        validation_report_uri (str): The URI of the Validation Report.
        shapes_graph_uri (str): The URI of the Shapes Graph.
        limit (int, optional): Maximum number of violations to return.
        offset (int, optional): Offset for the violations to return.
        executor (Optional[SparqlQueryExecutor]): Optional executor instance.
    
    Returns:
        dict: Property shape info with violations array containing detailed violation objects.
    """
    if executor is None:
        executor = get_default_executor()
    
    # OPTIMIZATION: Query shape details ONCE for this property shape (not per violation!)
    query = f"""
        SELECT DISTINCT ?nodeShape ?targetClass ?targetNode ?targetSubjectsOf ?targetObjectsOf
        FROM <{shapes_graph_uri}>
        WHERE {{
            ?nodeShape <http://www.w3.org/ns/shacl#property> <{property_shape}> .
            OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetClass> ?targetClass . }}
            OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetNode> ?targetNode . }}
            OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetSubjectsOf> ?targetSubjectsOf . }}
            OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetObjectsOf> ?targetObjectsOf . }}
        }}
    """
    shape_results = executor.execute_query(query, shapes_graph_uri, "get_shape_details")
    
    # Extract shape details once (reuse for all violations)
    node_shape = None
    target_class = None
    target_node = None
    target_subjects_of = None
    target_objects_of = None
    
    if shape_results["results"]["bindings"]:
        shape_binding = shape_results["results"]["bindings"][0]
        node_shape = shape_binding.get("nodeShape", {}).get("value")
        target_class = shape_binding.get("targetClass", {}).get("value")
        target_node = shape_binding.get("targetNode", {}).get("value")
        target_subjects_of = shape_binding.get("targetSubjectsOf", {}).get("value")
        target_objects_of = shape_binding.get("targetObjectsOf", {}).get("value")
    
    # Query for violations of this property shape
    query = f"""
        SELECT DISTINCT ?violation ?focusNode ?resultPath ?value ?message ?severity ?constraintComponent
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation a <http://www.w3.org/ns/shacl#ValidationResult> ;
                       <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                       <http://www.w3.org/ns/shacl#focusNode> ?focusNode ;
                       <http://www.w3.org/ns/shacl#resultPath> ?resultPath ;
                       <http://www.w3.org/ns/shacl#value> ?value ;
                       <http://www.w3.org/ns/shacl#resultMessage> ?message ;
                       <http://www.w3.org/ns/shacl#resultSeverity> ?severity ;
                       <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
        }}
    """
    if limit is not None:
        query += f" LIMIT {limit}"
    if offset is not None:
        query += f" OFFSET {offset}"
    
    try:
        results = executor.execute_query(query, validation_report_uri, "get_violations_for_property_shape")
    except Exception as e:
        raise RuntimeError(f"Error querying Validation Report: {str(e)}")
    
    # Process violations - use cached shape details
    violations = []
    for result in results["results"]["bindings"]:
        focus_node = result["focusNode"]["value"]
        result_path = result["resultPath"]["value"]
        value = result["value"]["value"]
        message = result["message"]["value"]
        severity = result["severity"]["value"]
        constraint_component = result["constraintComponent"]["value"]
        
        # Use the shape details queried once at the beginning
        violations.append({
            "focusNode": focus_node,
            "resultPath": result_path,
            "value": value,
            "message": message,
            "propertyShape": property_shape,
            "severity": severity,
            "targetClass": target_class,
            "targetNode": target_node,
            "targetSubjectsOf": target_subjects_of,
            "targetObjectsOf": target_objects_of,
            "nodeShape": node_shape,
            "constraintComponent": constraint_component
        })
    
    # Get summary stats for this property shape
    num_violations = executor.execute_count_query(
        f"""
        SELECT (COUNT(?violation) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> .
        }}
        """,
        validation_report_uri,
        "count_violations_for_property_shape_summary",
        "violationCount"
    )
    
    # Get constraint count
    num_constraints = executor.execute_count_query(
        f"""
        SELECT (COUNT(DISTINCT ?constraintComponent) AS ?constraintCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                       <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
        }}
        """,
        validation_report_uri,
        "count_constraints_for_property_shape_summary",
        "constraintCount"
    )
    
    # Get most violated constraint
    query = f"""
        SELECT ?constraintComponent (COUNT(?violation) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                       <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
        }}
        GROUP BY ?constraintComponent
        ORDER BY DESC(?violationCount)
        LIMIT 1
    """
    most_violated_results = executor.execute_query(query, validation_report_uri, "find_most_violated_constraint")
    most_violated_constraint = (
        most_violated_results["results"]["bindings"][0]["constraintComponent"]["value"]
        if most_violated_results["results"]["bindings"] else None
    )
    
    return {
        "PropertyShapeName": property_shape,
        "NumViolations": num_violations,
        "NumConstraints": num_constraints,
        "MostViolatedConstraint": most_violated_constraint,
        "Violations": violations
    }


def get_node_shape_with_violations(
    node_shape: str,
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI,
    limit_violations_per_property: int = None,
    offset_violations_per_property: int = None,
    executor: Optional[SparqlQueryExecutor] = None
) -> dict:
    """
    Get detailed information for a single node shape including all its property shapes with violations.
    
    Args:
        node_shape (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph.
        validation_report_uri (str): The URI of the Validation Report.
        limit_violations_per_property (int, optional): Max violations to return per property shape.
        offset_violations_per_property (int, optional): Offset for violations per property shape.
        executor (Optional[SparqlQueryExecutor]): Optional executor instance.
    
    Returns:
        dict: Node shape info with array of property shapes, each containing violation details.
    """
    if executor is None:
        executor = get_default_executor()
    
    # Get all property shapes for this node shape
    query = f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """
    
    try:
        shapes_results = executor.execute_query(query, shapes_graph_uri, "get_property_shapes_for_node")
    except Exception as e:
        raise RuntimeError(f"Error querying Shapes Graph: {str(e)}")
    
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]
    
    # Get detailed violations for each property shape
    property_shapes_with_violations = []
    for prop_shape in property_shapes:
        prop_shape_data = get_property_shape_with_violations(
            prop_shape,
            validation_report_uri=validation_report_uri,
            shapes_graph_uri=shapes_graph_uri,
            limit=limit_violations_per_property,
            offset=offset_violations_per_property,
            executor=executor
        )
        property_shapes_with_violations.append(prop_shape_data)
    
    return {
        "nodeShape": node_shape,
        "propertyShapes": property_shapes_with_violations
    }


def get_total_constraints_count_per_node_shape(shapes_graph_uri: str = SHAPES_GRAPH_URI, executor: Optional[SparqlQueryExecutor] = None) -> List[Dict[str, Any]]:
    """
    Calculate the total number of constraints (triples with predicates matching the SHACL features)
    for each Node Shape in the Shapes Graph.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        executor (Optional[SparqlQueryExecutor]): Optional executor instance.

    Returns:
        list: A JSON list where each element contains a Node Shape name and the total number of constraints.
    """
    if executor is None:
        executor = get_default_executor()
    

    # Build the SPARQL VALUES clause with full URIs for SHACL features
    shacl_features_values = " ".join([f"<{feature}>" for feature in SHACL_FEATURES])

    # SPARQL query to calculate total constraints (triples) per Node Shape
    query = f"""
        SELECT ?nodeShape (COUNT(*) AS ?totalConstraints)
        FROM <{shapes_graph_uri}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
            ?propertyShape ?constraintTriple ?object .
            VALUES ?constraintTriple {{ {shacl_features_values} }}
        }}
        GROUP BY ?nodeShape
        ORDER BY ?nodeShape
    """

    try:
        results = executor.execute_query(query, shapes_graph_uri, "get_total_constraints_per_node_shape")
    except Exception as e:
        raise RuntimeError(f"Error querying Shapes Graph: {str(e)}")

    # Process the results and build the JSON list
    constraints_per_node_shape = [
        {
            "NodeShapeName": result["nodeShape"]["value"],
            "NumConstraints": int(result["totalConstraints"]["value"])
        }
        for result in results["results"]["bindings"]
    ]

    return constraints_per_node_shape


def get_constraints_count_for_property_shapes(
    nodeshape_name: str,
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> List[Dict[str, Any]]:
    """
    Calculate the constraints count for each Property Shape associated with the given Node Shape
    using a single SPARQL query.

    Args:
        nodeshape_name (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        executor (Optional[SparqlQueryExecutor]): Optional executor instance.

    Returns:
        list: A JSON list containing Property Shape names and their corresponding constraints count.
    """
    if executor is None:
        executor = get_default_executor()
    
    # Build the SPARQL VALUES clause with SHACL features
    shacl_features_values = " ".join([f"<{feature}>" for feature in SHACL_FEATURES])

    # SPARQL query to calculate constraints count per Property Shape
    query = f"""
        SELECT ?propertyShape (COUNT(?constraintTriple) AS ?constraintCount)
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{nodeshape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
            ?propertyShape ?constraintTriple ?object .
            VALUES ?constraintTriple {{ {shacl_features_values} }}
        }}
        GROUP BY ?propertyShape
        ORDER BY ?propertyShape
    """

    try:
        results = executor.execute_query(query, shapes_graph_uri, "get_constraints_count_per_property_shape")
    except Exception as e:
        raise RuntimeError(f"Error querying constraints for Node Shape {nodeshape_name}: {str(e)}")

    # Process the results and build the JSON list
    property_shapes_constraints = [
        {
            "PropertyShapeName": result["propertyShape"]["value"],
            "NumConstraints": int(result["constraintCount"]["value"])
        }
        for result in results["results"]["bindings"]
    ]

    return property_shapes_constraints
