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

from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import os
from typing import List, Dict, Optional, Any
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI

logger = logging.getLogger(__name__)


def get_number_of_violations_in_validation_report(graph_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to get the total number of violations
    in the specified validation report graph.

    Args:
        graph_uri (str): The target validation report graph URI to query. Default is the global VALIDATION_REPORT_URI.

    Returns:
        int: The number of violations (sh:ValidationResult instances).
    """
    logger.info("Entering get_number_of_violations_in_validation_report", extra={'graph_uri': graph_uri})
    
    # Configure SPARQL query to count the number of sh:ValidationResult instances
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
    SELECT (COUNT(?violation) AS ?violationCount)
    FROM <{graph_uri}>
    WHERE {{
        ?report a <http://www.w3.org/ns/shacl#ValidationReport> ;
                <http://www.w3.org/ns/shacl#result> ?violation .
        ?violation a <http://www.w3.org/ns/shacl#ValidationResult> .
        }}
    """
    
    logger.debug("Executing SPARQL query", extra={'query': query, 'endpoint': ENDPOINT_URL})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()

        # Extract the count from the results
        violation_count = int(results["results"]["bindings"][0]["violationCount"]["value"])
        
        logger.info("Successfully retrieved violation count", extra={'violation_count': violation_count, 'graph_uri': graph_uri})
        return violation_count

    except Exception as e:
        logger.error("Error querying validation report", extra={'graph_uri': graph_uri, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error querying validation report: {str(e)}")


def get_number_of_node_shapes(graph_uri: str = SHAPES_GRAPH_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to get the number of Node Shapes
    in the specified shapes graph.

    Args:
        graph_uri (str): The target shapes graph URI to query. Default is "http://ex.org/ShapesGraph".

    Returns:
        int: The number of Node Shapes in the shapes graph.
    """
    logger.info("Entering get_number_of_node_shapes", extra={'graph_uri': graph_uri})
    
    # Configure SPARQL query to count Node Shapes
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT (COUNT(DISTINCT ?nodeShape) AS ?nodeShapesCount)
        FROM <{graph_uri}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> .
        }}
    """
    
    logger.debug("Executing SPARQL query to count node shapes", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the count from the results
    node_shapes_count = int(results["results"]["bindings"][0]["nodeShapesCount"]["value"])
    
    logger.info("Successfully retrieved node shapes count", extra={'node_shapes_count': node_shapes_count})
    return node_shapes_count 


def get_number_of_node_shapes_with_violations(shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Count how many sh:NodeShape in the Shapes Graph have at least one violation in the Validation Report.

    A NodeShape is counted if there exists a violation with sh:sourceShape pointing to:
      (a) one of its sh:property property shapes, OR
      (b) the node shape itself.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        int: Number of distinct NodeShapes with >= 1 violation.
    """
    logger.info("Entering get_number_of_node_shapes_with_violations", extra={'shapes_graph_uri': shapes_graph_uri, 'validation_report_uri': validation_report_uri})
    
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
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
    
    logger.debug("Executing SPARQL query to count node shapes with violations", extra={'query': query, 'endpoint': ENDPOINT_URL})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()

        # Extract the count from the results
        violated_node_shapes_count = int(results["results"]["bindings"][0]["violatedNodeShapesCount"]["value"])
        
        logger.info("Successfully retrieved node shapes with violations count", extra={'violated_count': violated_node_shapes_count})
        return violated_node_shapes_count
    except Exception as e:
        logger.error("Error querying node shapes with violations", extra={'shapes_graph_uri': shapes_graph_uri, 'validation_report_uri': validation_report_uri, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error querying node shapes with violations: {str(e)}")


def get_number_of_paths_in_shapes_graph(graph_uri: str = SHAPES_GRAPH_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of unique paths (sh:path values)
    in the Shapes Graph.

    Args:
        graph_uri (str): The URI of the Shapes Graph to query. Default is "http://ex.org/ShapesGraph".

    Returns:
        int: The number of unique sh:path values in the Shapes Graph.
    """
    logger.info("Entering get_number_of_paths_in_shapes_graph", extra={'graph_uri': graph_uri})
    
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT (COUNT(DISTINCT ?path) AS ?pathCount)
        FROM <{graph_uri}>
        WHERE {{
            ?propertyShape <http://www.w3.org/ns/shacl#path> ?path .
        }}
    """
    
    logger.debug("Executing SPARQL query to count paths", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()

        # Extract the count of unique paths
        path_count = int(results["results"]["bindings"][0]["pathCount"]["value"])
        
        logger.info("Successfully retrieved path count", extra={'path_count': path_count})
        return path_count
    except Exception as e:
        logger.error("Error querying paths in shapes graph", extra={'graph_uri': graph_uri, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error querying paths in shapes graph: {str(e)}")


def get_number_of_paths_with_violations(validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of unique paths (sh:resultPath values)
    in the Validation Report that caused violations.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of unique sh:resultPath values in the Validation Report.
    """
    logger.info("Entering get_number_of_paths_with_violations", extra={'validation_report_uri': validation_report_uri})
    
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT (COUNT(DISTINCT ?path) AS ?pathCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#resultPath> ?path .
        }}
    """
    
    logger.debug("Executing SPARQL query to count paths with violations", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()

        # Extract the count of unique paths
        path_count = int(results["results"]["bindings"][0]["pathCount"]["value"])
        
        logger.info("Successfully retrieved paths with violations count", extra={'path_count': path_count})
        return path_count
    except Exception as e:
        logger.error("Error querying paths with violations", extra={'validation_report_uri': validation_report_uri, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error querying paths with violations: {str(e)}")


def get_number_of_focus_nodes_in_validation_report(validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of unique sh:focusNode values
    in the Validation Report.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of unique sh:focusNode values in the Validation Report.
    """
    logger.info("Entering get_number_of_focus_nodes_in_validation_report", extra={'validation_report_uri': validation_report_uri})
    
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
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
    
    logger.debug("Executing SPARQL query to count focus nodes", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()

        # Extract the count of unique focus nodes
        focus_node_count = int(results["results"]["bindings"][0]["focusNodeCount"]["value"])
        
        logger.info("Successfully retrieved focus node count", extra={'focus_node_count': focus_node_count})
        return focus_node_count
    except Exception as e:
        logger.error("Error querying focus nodes in validation report", extra={'validation_report_uri': validation_report_uri, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error querying focus nodes: {str(e)}")


def count_triples(validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to count the number of triples in the Validation Report.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of triples in the Validation Report.
    """
    logger.info("Entering count_triples", extra={'validation_report_uri': validation_report_uri})
    
    # Configure SPARQL query to count triples
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT (COUNT(*) AS ?tripleCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?s ?p ?o .
        }}
    """
    
    logger.debug("Executing SPARQL query to count triples", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()

        # Extract the count from the results
        triple_count = int(results["results"]["bindings"][0]["tripleCount"]["value"])
        
        logger.info("Successfully retrieved triple count", extra={'triple_count': triple_count})
        return triple_count
    except Exception as e:
        logger.error("Error counting triples", extra={'validation_report_uri': validation_report_uri, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error counting triples: {str(e)}")
