from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import os
from typing import Dict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI
import logging

logger = logging.getLogger(__name__)

"""
Node Shape Metrics Module

This module provides functions for calculating metrics and statistics
specific to node shapes, including violation counts, property path counts,
and constraint counts.

Key functions:
- get_property_to_node_map: Map property shapes to their parent node shapes
- get_number_of_violations_for_node_shape: Count violations for a specific node shape
- get_number_of_violated_focus_for_node_shape: Count unique violated focus nodes
- get_number_of_property_paths_for_node_shape: Count property paths for a node shape
- get_number_of_constraints_for_node_shape: Count constraints for a node shape
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
    logger.info("Entering get_number_of_violated_focus_for_node_shape", extra={
        'node_shape': node_shape,
        'shapes_graph_uri': shapes_graph_uri,
        'validation_report_uri': validation_report_uri
    })
    
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query1 = f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """
    
    logger.debug("Querying property shapes for node shape", extra={'query': query1})
    sparql.setQuery(query1)
    sparql.setReturnFormat(JSON)
    
    try:
        shapes_results = sparql.query().convert()

        # Extract the list of Property Shapes
        property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]
        
        logger.debug(f"Found {len(property_shapes)} property shapes for node shape")

        # If no Property Shapes are found, return 0 focus nodes
        if not property_shapes:
            logger.info("No property shapes found, returning 0 focus nodes")
            return 0

        # Prepare the list of Property Shapes as a SPARQL VALUES clause
        property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

        # Step 2: Query the Validation Report to count unique focus nodes for these Property Shapes
        query2 = f"""
            SELECT (COUNT(DISTINCT ?focusNode) AS ?focusNodeCount)
            FROM <{validation_report_uri}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape ;
                           <http://www.w3.org/ns/shacl#focusNode> ?focusNode .
                VALUES ?propertyShape {{ {property_shapes_values} }}
            }}
        """
        
        logger.debug("Querying violated focus nodes", extra={'query': query2})
        sparql.setQuery(query2)
        validation_results = sparql.query().convert()

        # Extract the count of unique focus nodes
        focus_node_count = int(validation_results["results"]["bindings"][0]["focusNodeCount"]["value"])
        
        logger.info("Successfully retrieved violated focus node count", extra={'focus_node_count': focus_node_count})
        return focus_node_count
    except Exception as e:
        logger.error("Error querying violated focus nodes for node shape", extra={
            'node_shape': node_shape,
            'error': str(e)
        }, exc_info=True)
        raise RuntimeError(f"Error querying violated focus nodes: {str(e)}")


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
    logger.info("Entering get_number_of_property_paths_for_node_shape", extra={'shape_name': shape_name, 'shapes_graph_uri': shapes_graph_uri})
    
    # Configure SPARQL query to count unique paths
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT (COUNT(DISTINCT ?path) AS ?pathCount)
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{shape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
            ?propertyShape <http://www.w3.org/ns/shacl#path> ?path .
        }}
    """
    
    logger.debug("Executing SPARQL query to count property paths", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()

        # Extract the count of unique paths
        path_count = int(results["results"]["bindings"][0]["pathCount"]["value"])
        
        logger.info("Successfully retrieved property paths count", extra={'path_count': path_count})
        return path_count
    except Exception as e:
        logger.error("Error querying property paths for node shape", extra={'shape_name': shape_name, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error querying property paths: {str(e)}")


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
