"""
Violation Analysis Service Module

This module provides functions for analyzing violations grouped by different entities
(node shapes, paths, and focus nodes). These functions return detailed violation counts
and are used for violation breakdown analysis on the dashboard.

Functions:
- get_violations_per_node_shape: Count violations for each node shape
- get_violations_per_path: Count violations for each property path
- get_violations_per_focus_node: Count violations for each focus node
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import os
from typing import List, Dict, Any
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI

logger = logging.getLogger(__name__)


def get_violations_per_node_shape(shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> List[Dict[str, Any]]:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of violations for each Node Shape
    in the Shapes Graph, based on the associated Property Shapes in the Validation Report.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph to query. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with keys 'NodeShapeName' and 'NumViolations'.
    """
    logger.info("Entering get_violations_per_node_shape", extra={
        'shapes_graph_uri': shapes_graph_uri,
        'validation_report_uri': validation_report_uri
    })
    
    # Configure SPARQL query to get Node Shapes and their associated Property Shapes
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT DISTINCT ?nodeShape ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """
    
    logger.debug("Querying node shapes and property shapes", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)
    shapes_results = sparql.query().convert()

    # Process Node Shapes and their Property Shapes
    node_shapes_map = {}
    for result in shapes_results["results"]["bindings"]:
        node_shape = result["nodeShape"]["value"]
        property_shape = result["propertyShape"]["value"]
        if node_shape not in node_shapes_map:
            node_shapes_map[node_shape] = []
        node_shapes_map[node_shape].append(property_shape)
    
    logger.debug(f"Found {len(node_shapes_map)} node shapes to process")

    # Initialize list to store the final result
    violations_per_node_shape = []

    # For each Node Shape, calculate the number of violations
    for node_shape, property_shapes in node_shapes_map.items():
        property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])
        violation_query = f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{validation_report_uri}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
                VALUES ?propertyShape {{ {property_shapes_values} }}
            }}
        """
        logger.debug(f"Querying violations for node shape: {node_shape}")
        sparql.setQuery(violation_query)
        validation_results = sparql.query().convert()

        # Extract the violation count for the current Node Shape
        violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])

        # Append the result to the list
        violations_per_node_shape.append({
            "NodeShapeName": node_shape,
            "NumViolations": violation_count
        })
    
    logger.info(f"Successfully retrieved violations for {len(violations_per_node_shape)} node shapes")
    return violations_per_node_shape


def get_violations_per_path(validation_report_uri: str = VALIDATION_REPORT_URI) -> List[Dict[str, Any]]:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of violations for each unique sh:resultPath
    in the Validation Report.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with keys 'PathName' and 'NumViolations'.
    """
    logger.info("Entering get_violations_per_path", extra={'validation_report_uri': validation_report_uri})
    
    # Configure SPARQL query to count violations per result path
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT ?path (COUNT(?violation) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#resultPath> ?path .
        }}
        GROUP BY ?path
        ORDER BY DESC(?violationCount)
    """
    
    logger.debug("Querying violations per path", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Build the JSON list from the results
    violations_per_path = [
        {
            "PathName": result["path"]["value"],
            "NumViolations": int(result["violationCount"]["value"])
        }
        for result in results["results"]["bindings"]
    ]
    
    logger.info(f"Successfully retrieved violations for {len(violations_per_path)} paths")
    return violations_per_path


def get_violations_per_focus_node(validation_report_uri: str = VALIDATION_REPORT_URI) -> List[Dict[str, Any]]:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of violations for each unique sh:focusNode
    in the Validation Report.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with keys 'FocusNodeName' and 'NumViolations'.
    """
    logger.info("Entering get_violations_per_focus_node", extra={'validation_report_uri': validation_report_uri})
    
    # Configure SPARQL query to count violations per focus node
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT ?focusNode (COUNT(?violation) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#focusNode> ?focusNode .
        }}
        GROUP BY ?focusNode
        ORDER BY DESC(?violationCount)
    """
    
    logger.debug("Querying violations per focus node", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Build the JSON list from the results
    violations_per_focus_node = [
        {
            "FocusNodeName": result["focusNode"]["value"],
            "NumViolations": int(result["violationCount"]["value"])
        }
        for result in results["results"]["bindings"]
    ]
    
    logger.info(f"Successfully retrieved violations for {len(violations_per_focus_node)} focus nodes")
    return violations_per_focus_node
