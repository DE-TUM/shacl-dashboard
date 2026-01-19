from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import os
from typing import List, Dict, Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI
import logging

logger = logging.getLogger(__name__)

"""
Shape Retrieval Module

This module provides functions for retrieving and mapping shapes from the
shapes graph, including property shape to node shape mappings and detailed
shape definitions.

Key functions:
- map_property_shapes_to_node_shapes: Map property shapes to node shapes
- get_shape_from_shapes_graph: Get shape definitions from shapes graph
- get_number_of_property_shapes_for_node_shape: Count property shapes
- get_most_violated_constraint_for_node_shape: Find most violated constraint
"""


def map_property_shapes_to_node_shapes(validation_report_uri: str = "http://ex.org/ValidationReport",
                                       shapes_graph_uri: str = "http://ex.org/ShapesGraph") -> List[Dict[str, str]]:
    """
    Map property shapes from the validation report to their corresponding node shapes in the shapes graph.

    Args:
        validation_report_uri (str): The URI of the validation report graph. Default is "http://ex.org/ValidationReport".
        shapes_graph_uri (str): The URI of the shapes graph. Default is "http://ex.org/ShapesGraph".

    Returns:
        List[Dict[str, str]]: A list of dictionaries mapping property shape URIs to node shape URIs.
    """
    # SPARQL query to get the mapping of property shapes to node shapes
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape ?nodeShape
        FROM <{validation_report_uri}>
        FROM <{shapes_graph_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
            ?nodeShape <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the mapping from the results
    shape_mapping = [
        {result["propertyShape"]["value"]: result["nodeShape"]["value"]}
        for result in results["results"]["bindings"]
    ]

    return shape_mapping


def get_shape_from_shapes_graph(node_shape_names: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Query the Virtuoso SPARQL endpoint in two steps to avoid redundant triples:
    1. Query Node Shape triples.
    2. Query Property Shape triples for each Node Shape.

    Args:
        node_shape_names: A list of Node Shape URIs to query.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary representing the Node Shape tree structure.
        
    Example Output:
    {
        "http://example.org/PersonShape": {
            "triples": [
                {
                    "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                    "object": "http://www.w3.org/ns/shacl#NodeShape"
                },
                {
                    "predicate": "http://www.w3.org/ns/shacl#property",
                    "object": "http://example.org/PersonNamePropertyShape"
                }
            ],
            "propertyShapes": {
                "http://example.org/PersonNamePropertyShape": [
                    {
                        "predicate": "http://www.w3.org/ns/shacl#path",
                        "object": "http://example.org/name"
                    },
                    {
                        "predicate": "http://www.w3.org/ns/shacl#minCount",
                        "object": "1"
                    }
                ]
            }
        },
        "http://example.org/AddressShape": {
            "triples": [
                {
                    "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                    "object": "http://www.w3.org/ns/shacl#NodeShape"
                },
                {
                    "predicate": "http://www.w3.org/ns/shacl#property",
                    "object": "http://example.org/AddressStreetPropertyShape"
                }
            ],
            "propertyShapes": {
                "http://example.org/AddressStreetPropertyShape": [
                    {
                        "predicate": "http://www.w3.org/ns/shacl#path",
                        "object": "http://example.org/street"
                    },
                    {
                        "predicate": "http://www.w3.org/ns/shacl#minCount",
                        "object": "1"
                    }
                ]
            }
        }
    }
    """
    # Step 1: Query Node Shape triples
    node_shapes_values = " ".join([f"<{uri}>" for uri in node_shape_names])
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?subject ?predicate ?object
        FROM <{SHAPES_GRAPH_URI}>
        WHERE {{
            VALUES ?subject {{ {node_shapes_values} }}
            ?subject ?predicate ?object .
        }}
    """)
    sparql.setReturnFormat(JSON)
    node_shape_results = sparql.query().convert()

    # Process Node Shape triples into a structured dictionary
    shape_details = {}
    for result in node_shape_results["results"]["bindings"]:
        subject = result["subject"]["value"]
        predicate = result["predicate"]["value"]
        object_value = result["object"]["value"]

        if subject not in shape_details:
            shape_details[subject] = {
                "triples": [],
                "propertyShapes": {}
            }

        shape_details[subject]["triples"].append({
            "predicate": predicate,
            "object": object_value
        })

    # Step 2: Query Property Shape triples for each Node Shape
    property_shapes = {triple["object"] for shape in shape_details.values() for triple in shape["triples"] if triple["predicate"] == "http://www.w3.org/ns/shacl#property"}

    for property_shape in property_shapes:
        sparql.setQuery(f"""
            SELECT DISTINCT ?predicate ?object
            FROM <{SHAPES_GRAPH_URI}>
            WHERE {{
                <{property_shape}> ?predicate ?object .
            }}
        """)
        sparql.setReturnFormat(JSON)
        property_shape_results = sparql.query().convert()

        # Add Property Shape details to the corresponding Node Shape
        for result in property_shape_results["results"]["bindings"]:
            predicate = result["predicate"]["value"]
            object_value = result["object"]["value"]

            for node_shape, details in shape_details.items():
                if property_shape not in details["propertyShapes"]:
                    details["propertyShapes"][property_shape] = []

                details["propertyShapes"][property_shape].append({
                    "predicate": predicate,
                    "object": object_value
                })

    return shape_details


def get_number_of_property_shapes_for_node_shape(shape_name: str) -> int:
    """
    Query the Virtuoso SPARQL endpoint to get the number of Property Shapes
    associated with the given Node Shape from the Shapes Graph.

    Args:
        shape_name (str): The URI of the Node Shape to query.

    Returns:
        int: The number of Property Shapes associated with the Node Shape.
    """
    # SPARQL query to count the number of Property Shapes
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?propertyShape) AS ?propertyShapeCount)
        FROM <{SHAPES_GRAPH_URI}>
        WHERE {{
            <{shape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the number of Property Shapes
    property_shape_count = int(results["results"]["bindings"][0]["propertyShapeCount"]["value"])

    return property_shape_count


def get_most_violated_constraint_for_node_shape(shape_name: str) -> str:
    """
    Query the Virtuoso SPARQL endpoint to find the most frequently violated constraint
    (sh:sourceConstraintComponent) associated with the given Node Shape from the Validation Report.

    Args:
        shape_name (str): The URI of the Node Shape to query.

    Returns:
        str: The most frequently violated constraint component URI.

        - If there are no violations related to the given Node Shape, the function will return an empty string "".
    """
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape
        FROM <{SHAPES_GRAPH_URI}>
        WHERE {{
            <{shape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)
    shapes_results = sparql.query().convert()

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return an empty string
    if not property_shapes:
        return ""

    # Prepare the list of Property Shapes as a SPARQL VALUES clause
    property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

    # Step 2: Query the Validation Report to find the most violated constraint
    sparql.setQuery(f"""
        SELECT ?constraintComponent (COUNT(?violation) AS ?violationCount)
        FROM <{VALIDATION_REPORT_URI}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape ;
                       <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
            VALUES ?propertyShape {{ {property_shapes_values} }}
        }}
        GROUP BY ?constraintComponent
        ORDER BY DESC(?violationCount)
        LIMIT 1
    """)
    validation_results = sparql.query().convert()

    # Extract the most violated constraint component
    if validation_results["results"]["bindings"]:
        most_violated_constraint = validation_results["results"]["bindings"][0]["constraintComponent"]["value"]
        return most_violated_constraint

    # If no violations are found, return an empty string
    return ""
