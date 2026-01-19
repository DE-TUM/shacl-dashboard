from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import os
from typing import List, Dict, Optional, Any, Tuple
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI, SHACL_FEATURES
import math
import requests
import time 
import csv 
import logging

logger = logging.getLogger(__name__) 


"""
Shapes Overview Service Module

This module provides functions for analyzing and reporting on the overall structure
and content of the SHACL shapes graph. It extracts high-level information about
shapes definitions, their relationships, and structures to provide a comprehensive
overview of the validation schema.

The functions in this module support:
1. Retrieval of all shapes in the graph
2. Analysis of shape types and hierarchies
3. Mapping of property shapes to node shapes
4. Generation of summary statistics about constraints and violations
5. Analysis of constraint distribution across shapes
6. Calculation of violation metrics for shapes

Key functions:
- get_property_to_node_map: Map property shapes to their parent node shapes
- get_number_of_violations_for_node_shape: Count violations for a specific node shape
- get_property_shapes: Get property shapes for a specific node shape
- get_number_of_constraints_for_node_shape: Count constraints for a node shape
- get_node_shape_details_table: Generate detailed table of node shape information
- get_number_of_property_paths_for_node_shape: Count property paths for a node shape

Configuration:
- ENDPOINT_URL: SPARQL endpoint URL (default: http://localhost:8890/sparql)
- SHAPES_GRAPH_URI: URI for the shapes graph (default: http://ex.org/ShapesGraph)
- VALIDATION_REPORT_URI: URI for validation report (default: http://ex.org/ValidationReport)
- SHACL_FEATURES: List of SHACL constraint property URIs for analysis
"""


def get_property_to_node_map(shapes_graph_uri: str = SHAPES_GRAPH_URI) -> Dict[str, str]:
    """
    Map property shapes to their parent node shapes.
    
    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph.
    
    Returns:
        Dict[str, str]: Mapping of property shape URIs to node shape URIs.
    """
    logger.info("Entering get_property_to_node_map", extra={'shapes_graph_uri': shapes_graph_uri})
    
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT DISTINCT ?propertyShape ?nodeShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """
    
    logger.debug("Querying property to node mapping", extra={'query': query})
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    # Create a dictionary mapping property shapes to their node shapes
    prop_to_node_map = {}
    for result in results["results"]["bindings"]:
        prop_shape = result["propertyShape"]["value"]
        node_shape = result["nodeShape"]["value"]
        prop_to_node_map[prop_shape] = node_shape
    
    logger.info(f"Successfully mapped {len(prop_to_node_map)} property shapes to node shapes")
    return prop_to_node_map


def get_number_of_violations_for_node_shape(nodeshape_name: str, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of violations related to the given Node Shape.

    Args:
        nodeshape_name (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of violations related to the Node Shape.
    """
    logger.info("Entering get_number_of_violations_for_node_shape", extra={
        'nodeshape_name': nodeshape_name,
        'shapes_graph_uri': shapes_graph_uri,
        'validation_report_uri': validation_report_uri
    })
    
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    property_query = f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{nodeshape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """
    
    logger.debug("Querying property shapes for node shape", extra={'query': property_query})
    sparql.setQuery(property_query)
    sparql.setReturnFormat(JSON)
    shapes_results = sparql.query().convert()

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return 0 violations
    if not property_shapes:
        logger.info("No property shapes found for node shape, returning 0 violations")
        return 0

    # Prepare the list of Property Shapes as a SPARQL VALUES clause
    property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

    # Step 2: Query the Validation Report to count the number of violations for these Property Shapes
    violation_query = f"""
        SELECT (COUNT(?violation) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
            VALUES ?propertyShape {{ {property_shapes_values} }}
        }}
    """
    
    logger.debug("Counting violations for property shapes", extra={'query': violation_query, 'property_count': len(property_shapes)})
    sparql.setQuery(violation_query)
    validation_results = sparql.query().convert()

    # Extract the number of violations
    violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])
    
    logger.info(f"Found {violation_count} violations for node shape", extra={'violation_count': violation_count})
    return violation_count



def get_number_of_violated_focus_for_node_shape(node_shape: str, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of unique sh:focusNode values
    in the Validation Report that are violated due to the given Node Shape.

    Args:
        node_shape (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of unique sh:focusNode values related to violations caused by the Node Shape.
    """
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)
    shapes_results = sparql.query().convert()

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return 0 focus nodes
    if not property_shapes:
        return 0

    # Prepare the list of Property Shapes as a SPARQL VALUES clause
    property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

    # Step 2: Query the Validation Report to count unique focus nodes for these Property Shapes
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?focusNode) AS ?focusNodeCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape ;
                       <http://www.w3.org/ns/shacl#focusNode> ?focusNode .
            VALUES ?propertyShape {{ {property_shapes_values} }}
        }}
    """)
    validation_results = sparql.query().convert()

    # Extract the count of unique focus nodes
    focus_node_count = int(validation_results["results"]["bindings"][0]["focusNodeCount"]["value"])

    return focus_node_count



def get_number_of_property_paths_for_node_shape(shape_name: str, shapes_graph_uri: str = SHAPES_GRAPH_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of unique sh:path values
    for the given Node Shape in the Shapes Graph.

    Args:
        shape_name (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".

    Returns:
        int: The number of unique sh:path values for the Node Shape.
    """
    # Configure SPARQL query to count unique paths
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?path) AS ?pathCount)
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{shape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
            ?propertyShape <http://www.w3.org/ns/shacl#path> ?path .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the count of unique paths
    path_count = int(results["results"]["bindings"][0]["pathCount"]["value"])

    return path_count



def get_number_of_constraints_for_node_shape(node_shape_name: str, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to get the number of unique constraints
    (sh:sourceConstraintComponent) associated with the given Node Shape from the Validation Report.

    Args:
        node_shape_name (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of unique constraints associated with the Node Shape.
    """
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)

    try:
        shapes_results = sparql.query().convert()
    except Exception as e:
        raise RuntimeError(f"Error querying Shapes Graph: {str(e)}")

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return 0 constraints
    if not property_shapes:
        return 0

    # Prepare the list of Property Shapes as a SPARQL VALUES clause
    property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

    # Step 2: Query the Validation Report to count the unique constraints
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?constraintComponent) AS ?constraintCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape ;
                       <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
            VALUES ?propertyShape {{ {property_shapes_values} }}
        }}
    """)
    try:
        validation_results = sparql.query().convert()
    except Exception as e:
        raise RuntimeError(f"Error querying Validation Report: {str(e)}")

    # Extract the number of unique constraints
    constraint_count = int(validation_results["results"]["bindings"][0]["constraintCount"]["value"])

    return constraint_count



def get_property_shapes(node_shape: str, limit: Optional[int] = None, offset: Optional[int] = None, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> List[Dict[str, Any]]:
    """
    Retrieve Property Shapes associated with the given Node Shape, including statistics about violations,
    constraints, and the most violated constraint.

    Args:
        node_shape (str): The URI of the Node Shape to query.
        limit (int, optional): Maximum number of Property Shapes to return. Default is None (no limit).
        offset (int, optional): Offset for the Property Shapes to return. Default is None (no offset).
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list of Property Shapes with their statistics.
    """
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

    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        shapes_results = sparql.query().convert()
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
        sparql.setQuery(f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{validation_report_uri}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> .
            }}
        """)
        violation_results = sparql.query().convert()
        num_violations = int(violation_results["results"]["bindings"][0]["violationCount"]["value"])

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
            sparql.setQuery(f"""
                SELECT (COUNT(DISTINCT ?constraintComponent) AS ?constraintCount)
                FROM <{validation_report_uri}>
                WHERE {{
                    ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                            <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
                }}
            """)
            constraint_results = sparql.query().convert()
            num_constraints = int(constraint_results["results"]["bindings"][0]["constraintCount"]["value"])

            # Query the most violated constraint for the Property Shape
            sparql.setQuery(f"""
                SELECT ?constraintComponent (COUNT(?violation) AS ?violationCount)
                FROM <{validation_report_uri}>
                WHERE {{
                    ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                            <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
                }}
                GROUP BY ?constraintComponent
                ORDER BY DESC(?violationCount)
                LIMIT 1
            """)
            most_violated_results = sparql.query().convert()
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
) -> list:
    """
    Retrieve the number of violations per constraint type (sh:sourceConstraintComponent) for each
    Property Shape associated with the given Node Shape. Property Shapes with no violations are excluded.

    Args:
        node_shape (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list of Property Shapes with their violations categorized by constraints.
    """
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)

    try:
        shapes_results = sparql.query().convert()
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
        sparql.setQuery(f"""
            SELECT ?constraintComponent (COUNT(?violation) AS ?violationCount)
            FROM <{validation_report_uri}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                           <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
            }}
            GROUP BY ?constraintComponent
        """)
        sparql.setReturnFormat(JSON)

        try:
            violations_results = sparql.query().convert()
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
    offset: int = None
) -> Dict[str, Any]:
    """
    Get detailed violation information for a single property shape.
    
    Args:
        property_shape (str): The URI of the Property Shape to query.
        validation_report_uri (str): The URI of the Validation Report.
        shapes_graph_uri (str): The URI of the Shapes Graph.
        limit (int, optional): Maximum number of violations to return.
        offset (int, optional): Offset for the violations to return.
    
    Returns:
        dict: Property shape info with violations array containing detailed violation objects.
    """
    sparql = SPARQLWrapper(ENDPOINT_URL)
    
    # OPTIMIZATION: Query shape details ONCE for this property shape (not per violation!)
    sparql.setQuery(f"""
        SELECT DISTINCT ?nodeShape ?targetClass ?targetNode ?targetSubjectsOf ?targetObjectsOf
        FROM <{shapes_graph_uri}>
        WHERE {{
            ?nodeShape <http://www.w3.org/ns/shacl#property> <{property_shape}> .
            OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetClass> ?targetClass . }}
            OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetNode> ?targetNode . }}
            OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetSubjectsOf> ?targetSubjectsOf . }}
            OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetObjectsOf> ?targetObjectsOf . }}
        }}
    """)
    sparql.setReturnFormat(JSON)
    shape_results = sparql.query().convert()
    
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
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
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
    sparql.setQuery(f"""
        SELECT (COUNT(?violation) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> .
        }}
    """)
    violation_count_results = sparql.query().convert()
    num_violations = int(violation_count_results["results"]["bindings"][0]["violationCount"]["value"])
    
    # Get constraint count
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?constraintComponent) AS ?constraintCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                       <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
        }}
    """)
    constraint_count_results = sparql.query().convert()
    num_constraints = int(constraint_count_results["results"]["bindings"][0]["constraintCount"]["value"])
    
    # Get most violated constraint
    sparql.setQuery(f"""
        SELECT ?constraintComponent (COUNT(?violation) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                       <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
        }}
        GROUP BY ?constraintComponent
        ORDER BY DESC(?violationCount)
        LIMIT 1
    """)
    most_violated_results = sparql.query().convert()
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
    offset_violations_per_property: int = None
) -> dict:
    """
    Get detailed information for a single node shape including all its property shapes with violations.
    
    Args:
        node_shape (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph.
        validation_report_uri (str): The URI of the Validation Report.
        limit_violations_per_property (int, optional): Max violations to return per property shape.
        offset_violations_per_property (int, optional): Offset for violations per property shape.
    
    Returns:
        dict: Node shape info with array of property shapes, each containing violation details.
    """
    sparql = SPARQLWrapper(ENDPOINT_URL)
    
    # Get all property shapes for this node shape
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)
    
    try:
        shapes_results = sparql.query().convert()
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
            offset=offset_violations_per_property
        )
        property_shapes_with_violations.append(prop_shape_data)
    
    return {
        "nodeShape": node_shape,
        "propertyShapes": property_shapes_with_violations
    }


def get_total_constraints_count_per_node_shape(shapes_graph_uri: str = SHAPES_GRAPH_URI) -> List[Dict[str, Any]]:
    """
    Calculate the total number of constraints (triples with predicates matching the SHACL features)
    for each Node Shape in the Shapes Graph.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".

    Returns:
        list: A JSON list where each element contains a Node Shape name and the total number of constraints.
    """
    

    # Build the SPARQL VALUES clause with full URIs for SHACL features
    shacl_features_values = " ".join([f"<{feature}>" for feature in SHACL_FEATURES])

    # SPARQL query to calculate total constraints (triples) per Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
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
    """)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
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
    shapes_graph_uri: str = SHAPES_GRAPH_URI
) -> List[Dict[str, Any]]:
    """
    Calculate the constraints count for each Property Shape associated with the given Node Shape
    using a single SPARQL query.

    Args:
        nodeshape_name (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".

    Returns:
        list: A JSON list containing Property Shape names and their corresponding constraints count.
    """
    # Build the SPARQL VALUES clause with SHACL features
    shacl_features_values = " ".join([f"<{feature}>" for feature in SHACL_FEATURES])

    # SPARQL query to calculate constraints count per Property Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT ?propertyShape (COUNT(?constraintTriple) AS ?constraintCount)
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{nodeshape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
            ?propertyShape ?constraintTriple ?object .
            VALUES ?constraintTriple {{ {shacl_features_values} }}
        }}
        GROUP BY ?propertyShape
        ORDER BY ?propertyShape
    """)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
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


def get_maximum_number_of_violations_in_validation_report_for_node_shape() -> Dict[str, Any]:
    """
    Calculate the number of violations for each Node Shape, and find the Node Shape
    with the maximum number of violations.

    Returns:
        dict: A dictionary containing the Node Shape URI and the corresponding
        maximum number of violations, in the format:
        {
            "nodeShape": "<Node Shape URI>",
            "violationCount": <number of violations>
        }
    """
    # Step 1: Query the Shapes Graph to get all Node Shapes and their Property Shapes
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?nodeShape ?propertyShape
        FROM <{SHAPES_GRAPH_URI}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)
    node_shapes_results = sparql.query().convert()

    # Process Node Shapes and their Property Shapes
    node_shapes_map = {}
    for result in node_shapes_results["results"]["bindings"]:
        node_shape = result["nodeShape"]["value"]
        property_shape = result["propertyShape"]["value"]
        if node_shape not in node_shapes_map:
            node_shapes_map[node_shape] = []
        node_shapes_map[node_shape].append(property_shape)

    # Step 2: Query the Validation Report to count violations for each Property Shape
    violation_counts = {}
    for node_shape, property_shapes in node_shapes_map.items():
        property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])
        sparql.setQuery(f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{VALIDATION_REPORT_URI}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
                VALUES ?propertyShape {{ {property_shapes_values} }}
            }}
        """)
        validation_results = sparql.query().convert()

        # Extract the number of violations
        violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])
        violation_counts[node_shape] = violation_count

    # Step 3: Find the Node Shape with the maximum number of violations
    if violation_counts:
        max_node_shape = max(violation_counts, key=violation_counts.get)
        return {"nodeShape": max_node_shape, "violationCount": violation_counts[max_node_shape]}

    # If no violations are found, return an empty result
    return {"nodeShape": "", "violationCount": 0}

def get_average_number_of_violations_in_validation_report_for_node_shape() -> float:
    """
    Query the Virtuoso SPARQL endpoint to calculate the average number of violations
    caused by the Property Shapes of all Node Shapes from the Validation Report.

    Returns:
        float: The average number of violations per Node Shape.
        - The result is rounded to 2 decimal places
    """
    # Step 1: Query the Shapes Graph to get all Node Shapes and their Property Shapes
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?nodeShape ?propertyShape
        FROM <{SHAPES_GRAPH_URI}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)
    node_shapes_results = sparql.query().convert()

    # Process Node Shapes and their Property Shapes
    node_shapes_map = {}
    for result in node_shapes_results["results"]["bindings"]:
        node_shape = result["nodeShape"]["value"]
        property_shape = result["propertyShape"]["value"]
        if node_shape not in node_shapes_map:
            node_shapes_map[node_shape] = []
        node_shapes_map[node_shape].append(property_shape)

    # Step 2: Query the Validation Report to count violations for each Property Shape
    total_violations = 0
    total_node_shapes = len(node_shapes_map)

    for node_shape, property_shapes in node_shapes_map.items():
        property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])
        sparql.setQuery(f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{VALIDATION_REPORT_URI}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
                VALUES ?propertyShape {{ {property_shapes_values} }}
            }}
        """)
        validation_results = sparql.query().convert()

        # Extract the number of violations for this Node Shape
        violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])
        total_violations += violation_count

    # Step 3: Calculate the average number of violations
    if total_node_shapes == 0:
        return 0.0  # Avoid division by zero

    average_violations = total_violations / total_node_shapes
    return round(average_violations, 2)


def get_distribution_of_violations_per_constraint(
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI,
    num_bins: int = 10,
) -> Dict[str, Any]:
    """
    Generate data for the "Distribution of Violations per Constraint" plot in a single SPARQL query.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph to query.
        validation_report_uri (str): The URI of the Validation Report to query.
        shacl_features (set): The set of SHACL constraint predicates.
        num_bins (int): Number of bins for the plot. Default is 10.

    Returns:
        dict: A dictionary containing labels and datasets for the plot.
    """

    # Convert SHACL_FEATURES set to a SPARQL-friendly FILTER list
    shacl_feature_list = "".join(
        f" <{feature}>," for feature in SHACL_FEATURES
    ).strip(",")

    # Single SPARQL query: sums constraints and violations for each Node Shape
    query = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    SELECT ?nodeShape
           (SUM(COALESCE(?constraintsCount, 0)) AS ?totalConstraints)
           (SUM(COALESCE(?violationsCount, 0)) AS ?totalViolations)
    WHERE {{
      # NodeShape and propertyShape from the shapes graph
      GRAPH <{shapes_graph_uri}> {{
        ?nodeShape a sh:NodeShape ;
                   sh:property ?propertyShape .
      }}

      OPTIONAL {{
        # Sub-select for constraints
        SELECT ?propertyShape (COUNT(*) AS ?constraintsCount)
        WHERE {{
          GRAPH <{shapes_graph_uri}> {{
            ?propertyShape ?predicate ?obj .
            FILTER(?predicate IN (
              {shacl_feature_list}
            ))
          }}
        }}
        GROUP BY ?propertyShape
      }}

      OPTIONAL {{
        # Sub-select for violations
        SELECT ?propertyShape (COUNT(*) AS ?violationsCount)
        WHERE {{
          GRAPH <{validation_report_uri}> {{
            ?violation sh:sourceShape ?propertyShape .
          }}
        }}
        GROUP BY ?propertyShape
      }}
    }}
    GROUP BY ?nodeShape
    """

    # Execute SPARQL query
    response = requests.get(
        ENDPOINT_URL,
        params={"query": query, "format": "json"},
    )
    response.raise_for_status()
    results = response.json()["results"]["bindings"]

    # Compute ratio = totalViolations / totalConstraints for each NodeShape
    ratios = []
    for row in results:
        total_constraints = float(row["totalConstraints"]["value"])
        total_violations = float(row["totalViolations"]["value"])
        if total_constraints > 0:
            ratio = total_violations / total_constraints
            ratios.append(ratio)

    # Determine bins
    max_value = max(ratios, default=0)
    if max_value == 0:
        # If everything is zero, produce trivial data
        return {
            "labels": [f"0-0" for _ in range(num_bins)],
            "datasets": [
                {
                    "label": "Frequency",
                    "data": [0]*num_bins,
                }
            ],
        }

    bin_size = math.ceil(max_value / num_bins)
    labels = [f"{i}-{i + bin_size - 1}" for i in range(0, bin_size * num_bins, bin_size)]
    frequencies = [0] * num_bins

    # Populate bins
    for ratio in ratios:
        bin_index = min(int(ratio // bin_size), num_bins - 1)
        frequencies[bin_index] += 1

    # Prepare final data structure
    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Frequency",
                "data": frequencies,
            }
        ],
    }


def calculate_shannon_entropy(violation_counts: Dict[str, int]) -> float:
    total = sum(violation_counts.values())
    if total == 0:
        return 0.0
    probabilities = [count / total for count in violation_counts.values()]
    return sum(-p * math.log2(p) for p in probabilities if p > 0)


def get_correlation_of_constraints_and_violations(
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI,
) -> List[Dict[str, Any]]:
    """
    Provide data for a 'Correlation Between Constraints and Violations' plot (OPTIMIZED - NO OPTIONALS).
    For each Node Shape, it returns:
      - violation_entropy: Shannon entropy of the distribution of sourceConstraintComponent
      - num_violations: total number of violations for the Node Shape
      - num_constraints: total number of constraints in the Node Shape

    Returns a list of dicts, e.g.:
    [
      {
        'violation_entropy': 0.85,
        'num_violations': 15,
        'num_constraints': 18
      },
      ...
    ]
    """
    
    # Query 1: Get node shapes and their property shapes
    shapes_query = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    SELECT ?nodeShape ?propertyShape
    WHERE {{
      GRAPH <{shapes_graph_uri}> {{
        ?nodeShape a sh:NodeShape ;
                   sh:property ?propertyShape .
      }}
    }}
    """
    
    try:
        response = requests.get(ENDPOINT_URL, params={"query": shapes_query, "format": "json"}, timeout=30)
        response.raise_for_status()
        results = response.json()["results"]["bindings"]

        # Group property shapes by node shape
        node_shapes_map = {}
        all_property_shapes = set()
        
        for row in results:
            node_shape = row["nodeShape"]["value"]
            property_shape = row["propertyShape"]["value"]
            
            if node_shape not in node_shapes_map:
                node_shapes_map[node_shape] = []
            
            node_shapes_map[node_shape].append(property_shape)
            all_property_shapes.add(property_shape)

        # Query 2: Get constraints for all property shapes in batches
        constraints_by_prop = {}
        prop_list = list(all_property_shapes)
        batch_size = 100
        
        for i in range(0, len(prop_list), batch_size):
            batch = prop_list[i:i + batch_size]
            prop_values = " ".join([f"<{ps}>" for ps in batch])
            
            constraints_query = f"""
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            SELECT ?propertyShape ?predicate
            WHERE {{
              GRAPH <{shapes_graph_uri}> {{
                ?propertyShape ?predicate ?object .
                VALUES ?propertyShape {{ {prop_values} }}
              }}
            }}
            """
            
            try:
                resp = requests.get(ENDPOINT_URL, params={"query": constraints_query, "format": "json"}, timeout=30)
                resp.raise_for_status()
                const_results = resp.json()["results"]["bindings"]
                
                for row in const_results:
                    ps = row["propertyShape"]["value"]
                    predicate = row["predicate"]["value"]
                    
                    if ps not in constraints_by_prop:
                        constraints_by_prop[ps] = set()
                    
                    if predicate in SHACL_FEATURES:
                        constraints_by_prop[ps].add(predicate)
            except Exception as e:
                logger.error("Error fetching constraints batch %d: %s", i, str(e))
                continue

        # Query 3: Get violations grouped by constraint component in batches
        violations_by_prop = {}
        
        for i in range(0, len(prop_list), batch_size):
            batch = prop_list[i:i + batch_size]
            prop_values = " ".join([f"<{ps}>" for ps in batch])
            
            violations_query = f"""
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            SELECT ?propertyShape ?constraintComponent (COUNT(*) AS ?count)
            WHERE {{
              GRAPH <{validation_report_uri}> {{
                ?violation sh:sourceShape ?propertyShape ;
                           sh:sourceConstraintComponent ?constraintComponent .
                VALUES ?propertyShape {{ {prop_values} }}
              }}
            }}
            GROUP BY ?propertyShape ?constraintComponent
            """
            
            try:
                resp = requests.get(ENDPOINT_URL, params={"query": violations_query, "format": "json"}, timeout=30)
                resp.raise_for_status()
                viol_results = resp.json()["results"]["bindings"]
                
                for row in viol_results:
                    ps = row["propertyShape"]["value"]
                    constraint = row["constraintComponent"]["value"]
                    count = int(row["count"]["value"])
                    
                    if ps not in violations_by_prop:
                        violations_by_prop[ps] = {}
                    
                    violations_by_prop[ps][constraint] = violations_by_prop[ps].get(constraint, 0) + count
            except Exception as e:
                logger.error("Error fetching violations batch %d: %s", i, str(e))
                continue

        # Aggregate data for each node shape
        result_data = []
        
        for node_shape, property_shapes in node_shapes_map.items():
            total_constraints = 0
            violation_distribution = {}
            total_violations = 0
            
            for ps in property_shapes:
                # Count constraints
                total_constraints += len(constraints_by_prop.get(ps, set()))
                
                # Accumulate violations
                if ps in violations_by_prop:
                    for constraint, count in violations_by_prop[ps].items():
                        violation_distribution[constraint] = violation_distribution.get(constraint, 0) + count
                        total_violations += count
            
            # Calculate entropy
            violation_entropy = calculate_shannon_entropy(violation_distribution)
            
            entry = {
                "violation_entropy": round(violation_entropy, 2),
                "num_violations": total_violations,
                "num_constraints": total_constraints
            }
            result_data.append(entry)

        return result_data
        
    except requests.exceptions.RequestException as e:
        logger.error("Error executing SPARQL query: %s", str(e))
        raise RuntimeError(f"Failed to fetch correlation data: {str(e)}")




def get_node_shape_details_table(limit: Optional[int] = None, offset: Optional[int] = None, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> List[Dict[str, Any]]:
    """
    Generate data for the Node Shape Details table (OPTIMIZED WITH SIMPLE QUERIES).
    
    Uses 2-3 simple queries without OPTIONAL clauses to avoid timeouts.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph.
        validation_report_uri (str): The URI of the Validation Report.
        limit (int): The maximum number of results to return. Default is None (no limit).
        offset (int): The number of results to skip before starting to return results. Default is None (no offset).

    Returns:
        list: A list of dictionaries containing Node Shape details.
    """

    # Query 1: Get node shapes with property shape and path counts (simple, no joins)
    shapes_query = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    SELECT ?nodeShape 
           (COUNT(DISTINCT ?propertyShape) AS ?propertyShapeCount)
           (COUNT(DISTINCT ?path) AS ?propertyPathCount)
    WHERE {{
      GRAPH <{shapes_graph_uri}> {{
        ?nodeShape a sh:NodeShape ;
                   sh:property ?propertyShape .
        ?propertyShape sh:path ?path .
      }}
    }}
    GROUP BY ?nodeShape
    ORDER BY ?nodeShape
    """
    
    # Apply limit/offset to shapes query
    if limit is not None:
        shapes_query += f" LIMIT {limit}"
    if offset is not None:
        shapes_query += f" OFFSET {offset}"

    try:
        # Get node shapes
        response = requests.get(ENDPOINT_URL, params={"query": shapes_query, "format": "json"}, timeout=30)
        response.raise_for_status()
        shapes_results = response.json()["results"]["bindings"]

        # Build map of node shapes
        node_shapes_data = {}
        all_property_shapes = []
        
        for row in shapes_results:
            node_shape = row["nodeShape"]["value"]
            property_shape_count = int(row["propertyShapeCount"]["value"])
            property_path_count = int(row["propertyPathCount"]["value"])
            
            node_shapes_data[node_shape] = {
                "propertyShapeCount": property_shape_count,
                "propertyPathCount": property_path_count,
                "violations": 0,
                "focusNodes": 0,
                "mostViolatedConstraint": "None",
                "propertyShapes": []
            }
        
        # Query 2: Get property shapes for selected node shapes
        if node_shapes_data:
            node_shape_values = " ".join([f"<{ns}>" for ns in node_shapes_data.keys()])
            prop_shapes_query = f"""
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            SELECT ?nodeShape ?propertyShape
            WHERE {{
              GRAPH <{shapes_graph_uri}> {{
                ?nodeShape a sh:NodeShape ;
                           sh:property ?propertyShape .
                VALUES ?nodeShape {{ {node_shape_values} }}
              }}
            }}
            """
            
            prop_response = requests.get(ENDPOINT_URL, params={"query": prop_shapes_query, "format": "json"}, timeout=30)
            prop_response.raise_for_status()
            prop_results = prop_response.json()["results"]["bindings"]
            
            for row in prop_results:
                node_shape = row["nodeShape"]["value"]
                property_shape = row["propertyShape"]["value"]
                node_shapes_data[node_shape]["propertyShapes"].append(property_shape)
                all_property_shapes.append(property_shape)

        # Query 3: Get violations in batches (no OPTIONAL, simple aggregation)
        if all_property_shapes:
            unique_props = list(set(all_property_shapes))
            batch_size = 50
            
            violations_by_prop = {}
            constraint_counts_by_prop = {}
            
            for i in range(0, len(unique_props), batch_size):
                batch = unique_props[i:i + batch_size]
                prop_values = " ".join([f"<{ps}>" for ps in batch])
                
                viol_query = f"""
                PREFIX sh: <http://www.w3.org/ns/shacl#>
                SELECT ?propertyShape ?constraintComponent 
                       (COUNT(DISTINCT ?focusNode) AS ?focusCount)
                       (COUNT(*) AS ?violCount)
                WHERE {{
                  GRAPH <{validation_report_uri}> {{
                    ?violation sh:sourceShape ?propertyShape ;
                               sh:sourceConstraintComponent ?constraintComponent ;
                               sh:focusNode ?focusNode .
                    VALUES ?propertyShape {{ {prop_values} }}
                  }}
                }}
                GROUP BY ?propertyShape ?constraintComponent
                """
                
                try:
                    viol_response = requests.get(ENDPOINT_URL, params={"query": viol_query, "format": "json"}, timeout=30)
                    viol_response.raise_for_status()
                    viol_results = viol_response.json()["results"]["bindings"]
                    
                    for row in viol_results:
                        ps = row["propertyShape"]["value"]
                        constraint = row["constraintComponent"]["value"]
                        focus_count = int(row["focusCount"]["value"])
                        viol_count = int(row["violCount"]["value"])
                        
                        if ps not in violations_by_prop:
                            violations_by_prop[ps] = {"total": 0, "focusCount": 0}
                            constraint_counts_by_prop[ps] = {}
                        
                        violations_by_prop[ps]["total"] += viol_count
                        violations_by_prop[ps]["focusCount"] = max(violations_by_prop[ps]["focusCount"], focus_count)
                        constraint_counts_by_prop[ps][constraint] = constraint_counts_by_prop[ps].get(constraint, 0) + viol_count
                
                except Exception as e:
                    print(f"Error fetching violations batch {i}: {str(e)}")
                    continue

            # Aggregate violations back to node shapes
            for node_shape, data in node_shapes_data.items():
                total_violations = 0
                max_focus_nodes = 0
                all_constraints = {}
                
                for ps in data["propertyShapes"]:
                    if ps in violations_by_prop:
                        total_violations += violations_by_prop[ps]["total"]
                        max_focus_nodes = max(max_focus_nodes, violations_by_prop[ps]["focusCount"])
                        
                        for constraint, count in constraint_counts_by_prop.get(ps, {}).items():
                            all_constraints[constraint] = all_constraints.get(constraint, 0) + count
                
                data["violations"] = total_violations
                data["focusNodes"] = max_focus_nodes
                
                if all_constraints:
                    most_violated = max(all_constraints.items(), key=lambda x: x[1])
                    data["mostViolatedConstraint"] = most_violated[0].split("#")[-1]

        # Build final result
        node_shapes_details = []
        for idx, (node_shape, data) in enumerate(node_shapes_data.items(), start=1):
            violation_to_constraint_ratio = round(
                data["violations"] / data["propertyShapeCount"], 2
            ) if data["propertyShapeCount"] > 0 else 0.0

            node_shapes_details.append({
                "id": (offset if offset else 0) + idx,
                "name": node_shape,
                "violations": data["violations"],
                "propertyPaths": data["propertyPathCount"],
                "focusNodes": data["focusNodes"],
                "mostViolatedConstraint": data["mostViolatedConstraint"],
                "propertyShapes": data["propertyShapeCount"],
                "violationToConstraintRatio": violation_to_constraint_ratio,
            })

        return node_shapes_details

    except requests.exceptions.RequestException as e:
        logger.error("Error executing SPARQL query: %s", str(e))
        raise RuntimeError(f"Failed to fetch node shape details: {str(e)}")


def get_node_shape_with_most_unique_constraints(validation_report_uri: str = VALIDATION_REPORT_URI,
                                                shapes_graph_uri: str = SHAPES_GRAPH_URI) -> Dict[str, Any]:
    """
    Find the Node Shape that has the most unique constraint components (sh:sourceConstraintComponent) in the validation report.

    Args:
        validation_report_uri (str): The URI of the Validation Report.
        shapes_graph_uri (str): The URI of the Shapes Graph.

    Returns:
        dict: A dictionary containing the Node Shape with the most unique constraint components and its count.
              Example: {"nodeShape": "http://example.org/NodeShape1", "uniqueConstraintsCount": 15}
    """

    query = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    SELECT ?nodeShape (COUNT(DISTINCT ?constraintComponent) AS ?numConstraints)
    WHERE {{
      GRAPH <{shapes_graph_uri}> {{
        ?nodeShape a sh:NodeShape ;
                   sh:property ?propertyShape .
      }}
      GRAPH <{validation_report_uri}> {{
        ?violation sh:sourceShape ?propertyShape ;
                   sh:sourceConstraintComponent ?constraintComponent .
      }}
    }}
    GROUP BY ?nodeShape
    ORDER BY DESC(?numConstraints)
    LIMIT 1
    """

    # Execute the query
    response = requests.get(
        ENDPOINT_URL,
        params={"query": query, "format": "json"},
    )
    response.raise_for_status()
    results = response.json()["results"]["bindings"]

    # Process results
    if results:
        most_constrained_node_shape = results[0]["nodeShape"]["value"]
        constraint_count = int(results[0]["numConstraints"]["value"])
        return {"nodeShape": most_constrained_node_shape, "uniqueConstraintsCount": constraint_count}
    else:
        return {"nodeShape": None, "uniqueConstraintsCount": 0}




# def benchmark_function_execution_2(func, runs=10, csv_filename="execution_time_use_case_2_lkg3_schema2.csv"):
# #def benchmark_function_execution(func, runs=10, csv_filename="execution_time_test.csv"):
#     """
#     Measures the execution time of a function over multiple runs in milliseconds,
#     and saves results to a CSV.

#     Parameters:
#         func (callable): The function to benchmark.
#         runs (int): Number of times to run the function.
#         csv_filename (str): Name of the CSV file to save results.

#     Returns:
#         dict: A dictionary with 'times_ms', 'average_ms', and 'results'.
#     """
#     execution_times_ms = []
#     results = []

#     for i in range(runs):
#         start_time = time.time()
#         result = func()
#         end_time = time.time()

#         elapsed_ms = (end_time - start_time) * 1000  # Convert to milliseconds
#         execution_times_ms.append(elapsed_ms)
#         results.append(result)
#         print(f"Run {i+1}: {elapsed_ms:.2f} ms")

#     average_ms = sum(execution_times_ms) / runs
#     print(f"\nAverage execution time: {average_ms:.2f} ms")

#     # Save to CSV
#     with open(csv_filename, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["Run", "Execution Time (ms)"])
#         for idx, t in enumerate(execution_times_ms, start=1):
#             writer.writerow([idx, t])
#         writer.writerow(["Average", average_ms])

#     print(f"\nAll execution times and average saved to '{csv_filename}'")

#     return {
#         "times_ms": execution_times_ms,
#         "average_ms": average_ms,
#         "results": results
#     }
    
# def benchmark_function_execution_3(func, runs=10, csv_filename="execution_time_use_case_2_lkg3_schema2.csv"):
# #def benchmark_function_execution(func, runs=10, csv_filename="execution_time_test.csv"):
#     """
#     Measures the execution time of a function over multiple runs in milliseconds,
#     and saves results to a CSV.

#     Parameters:
#         func (callable): The function to benchmark.
#         runs (int): Number of times to run the function.
#         csv_filename (str): Name of the CSV file to save results.

#     Returns:
#         dict: A dictionary with 'times_ms', 'average_ms', and 'results'.
#     """
#     execution_times_ms = []
#     results = []

#     for i in range(runs):
#         start_time = time.time()
#         result = func()
#         end_time = time.time()

#         elapsed_ms = (end_time - start_time) * 1000  # Convert to milliseconds
#         execution_times_ms.append(elapsed_ms)
#         results.append(result)
#         print(f"Run {i+1}: {elapsed_ms:.2f} ms")

#     average_ms = sum(execution_times_ms) / runs
#     print(f"\nAverage execution time: {average_ms:.2f} ms")

#     # Save to CSV
#     with open(csv_filename, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["Run", "Execution Time (ms)"])
#         for idx, t in enumerate(execution_times_ms, start=1):
#             writer.writerow([idx, t])
#         writer.writerow(["Average", average_ms])

#     print(f"\nAll execution times and average saved to '{csv_filename}'")

#     return {
#         "times_ms": execution_times_ms,
#         "average_ms": average_ms,
#         "results": results
#     }
#print(get_correlation_of_constraints_and_violations())
# Execution Queries Use Case 2     
# benchmark_function_execution_2(get_correlation_of_constraints_and_violations)

# Execution Queries Use Case 3
# benchmark_function_execution_3(lambda: get_number_of_violations_per_constraint_type_for_property_shape("http://swat.cse.lehigh.edu/onto/univ-bench.owl#CourseShape"))

#print(get_number_of_violations_per_constraint_type_for_property_shape("http://swat.cse.lehigh.edu/onto/univ-bench.owl#CourseShape"))