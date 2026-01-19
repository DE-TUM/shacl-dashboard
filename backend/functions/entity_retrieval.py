from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import os
from typing import List, Dict, Union
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL
import logging

logger = logging.getLogger(__name__)

"""
Entity Retrieval Module

This module provides functions for retrieving various entities from the
validation report and shapes graph, including shape names, focus nodes,
property paths, and constraint components.

Key functions:
- get_all_shapes_names: Retrieve all shape names
- get_all_focus_node_names: Retrieve all focus node names
- get_all_property_path_names: Retrieve all property path names
- get_all_constraint_components_names: Retrieve all constraint component names
- get_violations_for_shape_name: Get violations for a specific shape
- get_number_of_shapes_in_shapes_graph: Count node and property shapes
- get_number_of_violations_in_validation_report: Count total violations
"""


def get_all_shapes_names(graph_uri: str = "http://ex.org/ValidationReport") -> List[str]:
    """
    Query the Virtuoso SPARQL endpoint to get all sh:sourceShape values
    from the specified graph.

    Args:
        graph_uri (str): The target graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        List[str]: A list of shape name URIs.
    """
    logger.info("Entering get_all_shapes_names", extra={'graph_uri': graph_uri})
    
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT DISTINCT ?shape
        FROM <{graph_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> ?shape .
        }}
    """
    
    logger.debug("Executing SPARQL query to get shape names", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()
        shapes = [result["shape"]["value"] for result in results["results"]["bindings"]]
        
        logger.info("Successfully retrieved shape names", extra={'shape_count': len(shapes)})
        return shapes
    except Exception as e:
        logger.error("Error querying shape names", extra={'graph_uri': graph_uri, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error querying shape names: {str(e)}")


def get_all_focus_node_names(graph_uri: str = "http://ex.org/ValidationReport") -> List[str]:
    """
    Query the Virtuoso SPARQL endpoint to get all sh:focusNode values
    from the specified graph.

    Args:
        graph_uri (str): The target graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        List[str]: A list of focus node URIs.
    """
    logger.info("Entering get_all_focus_node_names", extra={'graph_uri': graph_uri})
    
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT DISTINCT ?focusNode
        FROM <{graph_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#focusNode> ?focusNode .
        }}
    """
    
    logger.debug("Executing SPARQL query to get focus node names", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()
        focus_nodes = [result["focusNode"]["value"] for result in results["results"]["bindings"]]
        
        logger.info("Successfully retrieved focus node names", extra={'focus_node_count': len(focus_nodes)})
        return focus_nodes
    except Exception as e:
        logger.error("Error querying focus node names", extra={'graph_uri': graph_uri, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error querying focus node names: {str(e)}")


def get_all_property_path_names(graph_uri: str = "http://ex.org/ValidationReport") -> List[str]:
    """
    Query the Virtuoso SPARQL endpoint to get all sh:resultPath values
    from the specified graph.

    Args:
        graph_uri (str): The target graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        List[str]: A list of property path URIs.
    """
    logger.info("Entering get_all_property_path_names", extra={'graph_uri': graph_uri})
    
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT DISTINCT ?propertyPath
        FROM <{graph_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#resultPath> ?propertyPath .
        }}
    """
    
    logger.debug("Executing SPARQL query to get property path names", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()
        property_paths = [result["propertyPath"]["value"] for result in results["results"]["bindings"]]
        
        logger.info("Successfully retrieved property path names", extra={'property_path_count': len(property_paths)})
        return property_paths
    except Exception as e:
        logger.error("Error querying property path names", extra={'graph_uri': graph_uri, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error querying property path names: {str(e)}")


def get_all_constraint_components_names(graph_uri: str = "http://ex.org/ValidationReport") -> List[str]:
    """
    Query the Virtuoso SPARQL endpoint to get all sh:sourceConstraintComponent values
    from the specified graph.

    Args:
        graph_uri (str): The target graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        List[str]: A list of constraint component URIs.
    """
    logger.info("Entering get_all_constraint_components_names", extra={'graph_uri': graph_uri})
    
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
        SELECT DISTINCT ?constraintComponent
        FROM <{graph_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
        }}
    """
    
    logger.debug("Executing SPARQL query to get constraint component names", extra={'query': query})
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()
        constraint_components = [result["constraintComponent"]["value"] for result in results["results"]["bindings"]]
        
        logger.info("Successfully retrieved constraint component names", extra={'constraint_component_count': len(constraint_components)})
        return constraint_components
    except Exception as e:
        logger.error("Error querying constraint component names", extra={'graph_uri': graph_uri, 'error': str(e)}, exc_info=True)
        raise RuntimeError(f"Error querying constraint component names: {str(e)}")


def get_violations_for_shape_name(shape_name: Union[str, Dict[str, str]], graph_uri: str = "http://ex.org/ValidationReport") -> List[Dict[str, str]]:
    """
    Query the Virtuoso SPARQL endpoint to get all violations related to the specified property shape name.

    Args:
        shape_name: The shape name (URI) as a string or a dict with a 'shape' key.
        graph_uri: The target graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        List[Dict[str, str]]: A list of violation dictionaries with keys: focusNode, resultMessage, resultPath, resultSeverity, constraintComponent.
    """
    # Handle JSON input for shape_name
    if isinstance(shape_name, dict) and "shape" in shape_name:
        shape_name = shape_name["shape"]

    # Ensure the shape_name is a string
    if not isinstance(shape_name, str):
        raise ValueError("Invalid input: shape_name must be a string or a JSON object with a 'shape' key.")

    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT ?focusNode ?resultMessage ?resultPath ?resultSeverity ?constraintComponent
        FROM <{graph_uri}>
        WHERE {{
            ?violation a <http://www.w3.org/ns/shacl#ValidationResult> ;
                       <http://www.w3.org/ns/shacl#sourceShape> <{shape_name}> ;
                       <http://www.w3.org/ns/shacl#focusNode> ?focusNode ;
                       <http://www.w3.org/ns/shacl#resultMessage> ?resultMessage ;
                       <http://www.w3.org/ns/shacl#resultPath> ?resultPath ;
                       <http://www.w3.org/ns/shacl#resultSeverity> ?resultSeverity ;
                       <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract violations from the results
    violations = [
        {
            "focusNode": result["focusNode"]["value"],
            "resultMessage": result["resultMessage"]["value"],
            "resultPath": result["resultPath"]["value"],
            "resultSeverity": result["resultSeverity"]["value"],
            "constraintComponent": result["constraintComponent"]["value"]
        }
        for result in results["results"]["bindings"]
    ]

    return violations


def get_number_of_shapes_in_shapes_graph(graph_uri: str = "http://ex.org/ShapesGraph") -> Dict[str, int]:
    """
    Query the Virtuoso SPARQL endpoint to get the number of Node Shapes and Property Shapes
    in the specified shapes graph, including blank nodes.

    Args:
        graph_uri (str): The target shapes graph URI to query. Default is "http://ex.org/ShapesGraph".

    Returns:
        Dict[str, int]: A dictionary with keys 'nodeShapes' and 'propertyShapes' containing their counts.
    """
    # Configure SPARQL query to get the number of Node Shapes and Property Shapes (including blank nodes)
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT 
            (COUNT(DISTINCT ?nodeShape) AS ?nodeShapesCount)
            (COUNT(DISTINCT ?propertyShape) AS ?propertyShapesCount)
        FROM <{graph_uri}>
        WHERE {{
            OPTIONAL {{ ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> . }}
            OPTIONAL {{ ?shape <http://www.w3.org/ns/shacl#property> ?propertyShape . }}
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the counts from the results
    node_shapes_count = int(results["results"]["bindings"][0]["nodeShapesCount"]["value"])
    property_shapes_count = int(results["results"]["bindings"][0]["propertyShapesCount"]["value"])

    return {
        "nodeShapes": node_shapes_count,
        "propertyShapes": property_shapes_count
    }


def get_number_of_violations_in_validation_report(graph_uri: str = "http://ex.org/ValidationReport") -> int:
    """
    Query the Virtuoso SPARQL endpoint to get the total number of violations
    in the specified validation report graph.

    Args:
        graph_uri (str): The target validation report graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of violations (sh:ValidationResult instances).
    """
    # Configure SPARQL query to count the number of sh:ValidationResult instances
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT (COUNT(?violation) AS ?violationCount)
        FROM <{graph_uri}>
        WHERE {{
            ?violation a <http://www.w3.org/ns/shacl#ValidationResult> .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the count from the results
    violation_count = int(results["results"]["bindings"][0]["violationCount"]["value"])

    return violation_count
