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

import sys
import os
from typing import List, Dict, Any, Optional
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SHAPES_GRAPH_URI, VALIDATION_REPORT_URI
from sparql_executor import SparqlQueryExecutor, get_default_executor
from validators import validate_graph_uri, ValidationError

logger = logging.getLogger(__name__)


def get_violations_per_node_shape(
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> List[Dict[str, Any]]:
    """
    Query the SPARQL endpoint to calculate the number of violations for each Node Shape
    in the Shapes Graph, based on the associated Property Shapes in the Validation Report.

    Args:
        shapes_graph_uri: The URI of the Shapes Graph to query.
        validation_report_uri: The URI of the Validation Report to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided).

    Returns:
        A list of dictionaries with keys 'NodeShapeName' and 'NumViolations'.
    
    Raises:
        ValidationError: If any URI parameter is invalid.
    """
    # Validate inputs at service layer
    shapes_graph_uri = validate_graph_uri(shapes_graph_uri, "shapes_graph_uri")
    validation_report_uri = validate_graph_uri(validation_report_uri, "validation_report_uri")
    
    if executor is None:
        executor = get_default_executor()
    
    logger.info("Entering get_violations_per_node_shape", extra={
        'shapes_graph_uri': shapes_graph_uri,
        'validation_report_uri': validation_report_uri
    })
    
    # Get Node Shapes and their associated Property Shapes
    query = f"""
    SELECT DISTINCT ?nodeShape ?propertyShape
    FROM <{shapes_graph_uri}>
    WHERE {{
        ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                   <http://www.w3.org/ns/shacl#property> ?propertyShape .
    }}
    """
    
    shapes_results = executor.execute_query(
        query,
        graph_uri=shapes_graph_uri,
        operation_name="get_node_shapes_and_properties"
    )

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
        
        violation_count = executor.execute_count_query(
            violation_query,
            graph_uri=validation_report_uri,
            operation_name="get_violations_for_node_shape",
            count_var="violationCount"
        )

        violations_per_node_shape.append({
            "NodeShapeName": node_shape,
            "NumViolations": violation_count
        })
    
    logger.info(f"Successfully retrieved violations for {len(violations_per_node_shape)} node shapes")
    return violations_per_node_shape


def get_violations_per_path(
    validation_report_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> List[Dict[str, Any]]:
    """
    Query the SPARQL endpoint to calculate the number of violations for each unique sh:resultPath
    in the Validation Report.

    Args:
        validation_report_uri: The URI of the Validation Report to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided).

    Returns:
        A list of dictionaries with keys 'PathName' and 'NumViolations'.
    
    Raises:
        ValidationError: If validation_report_uri is invalid.
    """
    # Validate input at service layer
    validation_report_uri = validate_graph_uri(validation_report_uri, "validation_report_uri")
    
    if executor is None:
        executor = get_default_executor()
    
    logger.info("Entering get_violations_per_path", extra={'validation_report_uri': validation_report_uri})
    
    query = f"""
    SELECT ?path (COUNT(?violation) AS ?violationCount)
    FROM <{validation_report_uri}>
    WHERE {{
        ?violation <http://www.w3.org/ns/shacl#resultPath> ?path .
    }}
    GROUP BY ?path
    ORDER BY DESC(?violationCount)
    """
    
    results = executor.execute_query(
        query,
        graph_uri=validation_report_uri,
        operation_name="get_violations_per_path"
    )

    violations_per_path = [
        {
            "PathName": result["path"]["value"],
            "NumViolations": int(result["violationCount"]["value"])
        }
        for result in results["results"]["bindings"]
    ]
    
    logger.info(f"Successfully retrieved violations for {len(violations_per_path)} paths")
    return violations_per_path


def get_violations_per_focus_node(
    validation_report_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> List[Dict[str, Any]]:
    """
    Query the SPARQL endpoint to calculate the number of violations for each unique sh:focusNode
    in the Validation Report.

    Args:
        validation_report_uri: The URI of the Validation Report to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided).

    Returns:
        A list of dictionaries with keys 'FocusNodeName' and 'NumViolations'.
    
    Raises:
        ValidationError: If validation_report_uri is invalid.
    """
    # Validate input at service layer
    validation_report_uri = validate_graph_uri(validation_report_uri, "validation_report_uri")
    
    if executor is None:
        executor = get_default_executor()
    
    logger.info("Entering get_violations_per_focus_node", extra={'validation_report_uri': validation_report_uri})
    
    query = f"""
    SELECT ?focusNode (COUNT(?violation) AS ?violationCount)
    FROM <{validation_report_uri}>
    WHERE {{
        ?violation <http://www.w3.org/ns/shacl#focusNode> ?focusNode .
    }}
    GROUP BY ?focusNode
    ORDER BY DESC(?violationCount)
    """
    
    results = executor.execute_query(
        query,
        graph_uri=validation_report_uri,
        operation_name="get_violations_per_focus_node"
    )

    violations_per_focus_node = [
        {
            "FocusNodeName": result["focusNode"]["value"],
            "NumViolations": int(result["violationCount"]["value"])
        }
        for result in results["results"]["bindings"]
    ]
    
    logger.info(f"Successfully retrieved violations for {len(violations_per_focus_node)} focus nodes")
    return violations_per_focus_node
