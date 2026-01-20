import sys
import os
from typing import Dict, Any, Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SHAPES_GRAPH_URI, VALIDATION_REPORT_URI, ENDPOINT_URL
from sparql_executor import SparqlQueryExecutor, get_default_executor
import requests
import logging

logger = logging.getLogger(__name__)

"""
Shape Statistics Module

This module provides functions for calculating statistical information
about shapes, including maximum and average violation counts, and
identifying shapes with the most unique constraints.

Key functions:
- get_maximum_number_of_violations_in_validation_report_for_node_shape: Find shape with max violations
- get_average_number_of_violations_in_validation_report_for_node_shape: Calculate average violations
- get_node_shape_with_most_unique_constraints: Find shape with most unique constraints
"""


def get_maximum_number_of_violations_in_validation_report_for_node_shape(executor: Optional[SparqlQueryExecutor] = None) -> Dict[str, Any]:
    """
    Calculate the number of violations for each Node Shape, and find the Node Shape
    with the maximum number of violations.
    
    Args:
        executor (Optional[SparqlQueryExecutor]): Optional executor instance.

    Returns:
        dict: A dictionary containing the Node Shape URI and the corresponding
        maximum number of violations, in the format:
        {
            "nodeShape": "<Node Shape URI>",
            "violationCount": <number of violations>
        }
    """
    if executor is None:
        executor = get_default_executor()
    
    # Step 1: Query the Shapes Graph to get all Node Shapes and their Property Shapes
    query = f"""
        SELECT DISTINCT ?nodeShape ?propertyShape
        FROM <{SHAPES_GRAPH_URI}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """
    node_shapes_results = executor.execute_query(query, SHAPES_GRAPH_URI, "get_node_shapes_and_properties")

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
        query = f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{VALIDATION_REPORT_URI}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
                VALUES ?propertyShape {{ {property_shapes_values} }}
            }}
        """
        validation_results = executor.execute_query(query, VALIDATION_REPORT_URI, "count_violations_for_node_shape")

        # Extract the number of violations
        violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])
        violation_counts[node_shape] = violation_count

    # Step 3: Find the Node Shape with the maximum number of violations
    if violation_counts:
        max_node_shape = max(violation_counts, key=violation_counts.get)
        return {"nodeShape": max_node_shape, "violationCount": violation_counts[max_node_shape]}

    # If no violations are found, return an empty result
    return {"nodeShape": "", "violationCount": 0}


def get_average_number_of_violations_in_validation_report_for_node_shape(executor: Optional[SparqlQueryExecutor] = None) -> float:
    """
    Query the Virtuoso SPARQL endpoint to calculate the average number of violations
    caused by the Property Shapes of all Node Shapes from the Validation Report.
    
    Args:
        executor (Optional[SparqlQueryExecutor]): Optional executor instance.

    Returns:
        float: The average number of violations per Node Shape.
        - The result is rounded to 2 decimal places
    """
    if executor is None:
        executor = get_default_executor()
    
    # Step 1: Query the Shapes Graph to get all Node Shapes and their Property Shapes
    query = f"""
        SELECT DISTINCT ?nodeShape ?propertyShape
        FROM <{SHAPES_GRAPH_URI}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """
    node_shapes_results = executor.execute_query(query, SHAPES_GRAPH_URI, "get_node_shapes_and_properties")

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
        query = f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{VALIDATION_REPORT_URI}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
                VALUES ?propertyShape {{ {property_shapes_values} }}
            }}
        """
        validation_results = executor.execute_query(query, VALIDATION_REPORT_URI, "count_violations_for_average")

        # Extract the number of violations for this Node Shape
        violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])
        total_violations += violation_count

    # Step 3: Calculate the average number of violations
    if total_node_shapes == 0:
        return 0.0  # Avoid division by zero

    average_violations = total_violations / total_node_shapes
    return round(average_violations, 2)


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
