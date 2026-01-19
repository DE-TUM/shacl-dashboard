"""
Validation Statistics Service Module

This module provides basic statistical functions for querying counts and metrics from 
SHACL validation reports and shapes graphs. These functions return simple counts and 
are typically used for dashboard summary statistics.

Functions:
- get_number_of_violations_in_validation_report: Count total violations
- get_number_of_node_shapes: Count node shapes in shapes graph  
- get_number_of_node_shapes_with_violations: Count shapes with violations
- get_number_of_paths_in_shapes_graph: Count unique paths in shapes graph
- get_number_of_paths_with_violations: Count paths with violations
- get_number_of_focus_nodes_in_validation_report: Count unique focus nodes
- count_triples: Count total triples in validation report
"""

import sys
import os
from typing import Optional
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SHAPES_GRAPH_URI, VALIDATION_REPORT_URI
from sparql_executor import SparqlQueryExecutor, get_default_executor
from validators import validate_graph_uri, ValidationError

logger = logging.getLogger(__name__)


def get_number_of_violations_in_validation_report(
    graph_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> int:
    """
    Query the SPARQL endpoint to get the total number of violations
    in the specified validation report graph.

    Args:
        graph_uri: The target validation report graph URI to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided).

    Returns:
        The number of violations (sh:ValidationResult instances).
        
    Raises:
        ValidationError: If graph_uri is invalid.
    """
    # Validate input at service layer
    graph_uri = validate_graph_uri(graph_uri, "graph_uri")
    
    if executor is None:
        executor = get_default_executor()
    
    logger.info(
        "Getting violation count from validation report",
        extra={'function': 'get_number_of_violations_in_validation_report'}
    )
    
    query = f"""
    SELECT (COUNT(?violation) AS ?violationCount)
    FROM <{graph_uri}>
    WHERE {{
        ?report a <http://www.w3.org/ns/shacl#ValidationReport> ;
                <http://www.w3.org/ns/shacl#result> ?violation .
        ?violation a <http://www.w3.org/ns/shacl#ValidationResult> .
    }}
    """
    
    return executor.execute_count_query(
        query,
        graph_uri=graph_uri,
        operation_name="get_violation_count",
        count_var="violationCount"
    )


def get_number_of_node_shapes(
    graph_uri: str = SHAPES_GRAPH_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> int:
    """
    Query the SPARQL endpoint to get the number of Node Shapes
    in the specified shapes graph.

    Args:
        graph_uri: The target shapes graph URI to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided).

    Returns:
        The number of Node Shapes in the shapes graph.
        
    Raises:
        ValidationError: If graph_uri is invalid.
    """
    # Validate input at service layer
    graph_uri = validate_graph_uri(graph_uri, "graph_uri")
    
    if executor is None:
        executor = get_default_executor()
    
    logger.info("Entering get_number_of_node_shapes", extra={'graph_uri': graph_uri})
    
    query = f"""
    SELECT (COUNT(DISTINCT ?nodeShape) AS ?nodeShapesCount)
    FROM <{graph_uri}>
    WHERE {{
        ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> .
    }}
    """
    
    return executor.execute_count_query(
        query,
        graph_uri=graph_uri,
        operation_name="get_node_shapes_count",
        count_var="nodeShapesCount"
    ) 


def get_number_of_node_shapes_with_violations(
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> int:
    """
    Count how many sh:NodeShape in the Shapes Graph have at least one violation in the Validation Report.

    A NodeShape is counted if there exists a violation with sh:sourceShape pointing to:
      (a) one of its sh:property property shapes, OR
      (b) the node shape itself.

    Args:
        shapes_graph_uri: The URI of the Shapes Graph.
        validation_report_uri: The URI of the Validation Report.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided).

    Returns:
        Number of distinct NodeShapes with >= 1 violation.
        
    Raises:
        ValidationError: If any URI parameter is invalid.
    """
    # Validate inputs at service layer
    shapes_graph_uri = validate_graph_uri(shapes_graph_uri, "shapes_graph_uri")
    validation_report_uri = validate_graph_uri(validation_report_uri, "validation_report_uri")
    
    if executor is None:
        executor = get_default_executor()
    
    logger.info("Entering get_number_of_node_shapes_with_violations", extra={'shapes_graph_uri': shapes_graph_uri, 'validation_report_uri': validation_report_uri})
    
    query = f"""
    SELECT (COUNT(DISTINCT ?nodeShape) AS ?violatedNodeShapesCount)
    WHERE {{
        GRAPH <{shapes_graph_uri}> {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> .
            OPTIONAL {{
                ?nodeShape <http://www.w3.org/ns/shacl#property> ?propertyShape .
            }}
        }}
        GRAPH <{validation_report_uri}> {{
            {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?nodeShape .
            }}
            UNION
            {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
            }}
        }}
    }}
    """
    
    return executor.execute_count_query(
        query,
        graph_uri=shapes_graph_uri,
        operation_name="get_node_shapes_with_violations_count",
        count_var="violatedNodeShapesCount"
    )


def get_number_of_paths_in_shapes_graph(
    graph_uri: str = SHAPES_GRAPH_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> int:
    """
    Query the SPARQL endpoint to calculate the number of unique paths (sh:path values)
    in the Shapes Graph.

    Args:
        graph_uri: The URI of the Shapes Graph to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided).

    Returns:
        The number of unique sh:path values in the Shapes Graph.
        
    Raises:
        ValidationError: If graph_uri is invalid.
    """
    # Validate input at service layer
    graph_uri = validate_graph_uri(graph_uri, "graph_uri")
    
    if executor is None:
        executor = get_default_executor()
    
    logger.info("Entering get_number_of_paths_in_shapes_graph", extra={'graph_uri': graph_uri})
    
    query = f"""
    SELECT (COUNT(DISTINCT ?path) AS ?pathCount)
    FROM <{graph_uri}>
    WHERE {{
        ?propertyShape <http://www.w3.org/ns/shacl#path> ?path .
    }}
    """
    
    return executor.execute_count_query(
        query,
        graph_uri=graph_uri,
        operation_name="get_paths_count",
        count_var="pathCount"
    )


def get_number_of_paths_with_violations(
    validation_report_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> int:
    """
    Query the SPARQL endpoint to calculate the number of unique paths (sh:resultPath values)
    in the Validation Report that caused violations.

    Args:
        validation_report_uri: The URI of the Validation Report to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided).

    Returns:
        The number of unique sh:resultPath values in the Validation Report.
    """
    if executor is None:
        executor = get_default_executor()
    
    logger.info("Entering get_number_of_paths_with_violations", extra={'validation_report_uri': validation_report_uri})
    
    query = f"""
    SELECT (COUNT(DISTINCT ?path) AS ?pathCount)
    FROM <{validation_report_uri}>
    WHERE {{
        ?violation <http://www.w3.org/ns/shacl#resultPath> ?path .
    }}
    """
    
    return executor.execute_count_query(
        query,
        graph_uri=validation_report_uri,
        operation_name="get_paths_with_violations_count",
        count_var="pathCount"
    )


def get_number_of_focus_nodes_in_validation_report(
    validation_report_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> int:
    """
    Query the SPARQL endpoint to calculate the number of unique sh:focusNode values
    in the Validation Report.

    Args:
        validation_report_uri: The URI of the Validation Report to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided).

    Returns:
        The number of unique sh:focusNode values in the Validation Report.
    """
    if executor is None:
        executor = get_default_executor()
    
    logger.info("Entering get_number_of_focus_nodes_in_validation_report", extra={'validation_report_uri': validation_report_uri})
    
    query = f"""
    SELECT (COUNT(DISTINCT ?focusNode) AS ?focusNodeCount)
    FROM <{validation_report_uri}>
    WHERE {{
        ?report a <http://www.w3.org/ns/shacl#ValidationReport> ;
                <http://www.w3.org/ns/shacl#result> ?violation .

        ?violation a <http://www.w3.org/ns/shacl#ValidationResult> ;
                   <http://www.w3.org/ns/shacl#focusNode> ?focusNode .

        FILTER(isBlank(?violation))
    }}
    """
    
    return executor.execute_count_query(
        query,
        graph_uri=validation_report_uri,
        operation_name="get_focus_nodes_count",
        count_var="focusNodeCount"
    )


def count_triples(
    validation_report_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> int:
    """
    Query the SPARQL endpoint to count the number of triples in the Validation Report.

    Args:
        validation_report_uri: The URI of the Validation Report to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided).

    Returns:
        The number of triples in the Validation Report.
    """
    if executor is None:
        executor = get_default_executor()
    
    logger.info("Entering count_triples", extra={'validation_report_uri': validation_report_uri})
    
    query = f"""
    SELECT (COUNT(*) AS ?tripleCount)
    FROM <{validation_report_uri}>
    WHERE {{
        ?s ?p ?o .
    }}
    """
    
    return executor.execute_count_query(
        query,
        graph_uri=validation_report_uri,
        operation_name="count_triples",
        count_var="tripleCount"
    )
