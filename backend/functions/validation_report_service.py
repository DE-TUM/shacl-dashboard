from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import os
from typing import List, Dict, Optional, Any
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI, SHACL_FEATURES
import requests

logger = logging.getLogger(__name__)

"""
Validation Report Service Module

This module provides functions for generating detailed validation reports and finding 
the most violated entities (node shapes, paths, focus nodes) in SHACL validation reports.

Key functions:
- generate_validation_details_report: Generate comprehensive validation reports with shape details
- get_most_violated_node_shape: Find the node shape with the most violations
- get_most_violated_path: Find the path with the most violations
- get_most_violated_focus_node: Find the focus node with the most violations
- get_most_frequent_constraint_component: Find the most frequently triggered constraint component
- get_distinct_constraint_components_count: Count distinct constraint components in validation report
- get_distinct_constraints_count_in_shapes: Count distinct constraint types used in shapes graph
"""


def generate_validation_details_report(
    validation_report_uri: str = VALIDATION_REPORT_URI,
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Generate a detailed validation report with prefixes, violations, and shape details.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query.
        shapes_graph_uri (str): The URI of the Shapes Graph to query.
        limit (int): Maximum number of violations to return. Default is 10.
        offset (int): Offset for the violations to return. Default is 0.

    Returns:
        Dict[str, Any]: A dictionary containing 'prefixes' and 'violations' keys with detailed violation information.
    """
    from .utility_functions import get_prefixes_from_endpoint, parse_rdf_list
    
    # Step 1: Fetch prefixes
    prefixes = get_prefixes_from_endpoint(ENDPOINT_URL)

    # Step 2: Query validation report for violations
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?violation ?focusNode ?resultPath ?value ?message ?sourceShape ?severity ?constraintComponent
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation a <http://www.w3.org/ns/shacl#ValidationResult> ;
                       <http://www.w3.org/ns/shacl#focusNode> ?focusNode ;
                       <http://www.w3.org/ns/shacl#resultPath> ?resultPath ;
                       <http://www.w3.org/ns/shacl#value> ?value ;
                       <http://www.w3.org/ns/shacl#resultMessage> ?message ;
                       <http://www.w3.org/ns/shacl#sourceShape> ?sourceShape ;
                       <http://www.w3.org/ns/shacl#resultSeverity> ?severity ;
                       <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
        }}
        LIMIT {limit}
        OFFSET {offset}
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Process violations and fetch shape details
    violations = []
    for idx, result in enumerate(results["results"]["bindings"], start=1):
        focus_node = result["focusNode"]["value"]
        result_path = result["resultPath"]["value"]
        value = result["value"]["value"]
        message = result["message"]["value"]
        source_shape = result["sourceShape"]["value"]
        severity = result["severity"]["value"]
        constraint_component = result["constraintComponent"]["value"]

        # Query shapes graph for shape details
        sparql.setQuery(f"""
            SELECT DISTINCT ?nodeShape ?targetClass ?targetNode ?targetSubjectsOf ?targetObjectsOf
            FROM <{shapes_graph_uri}>
            WHERE {{
                ?nodeShape <http://www.w3.org/ns/shacl#property> <{source_shape}> .
                OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetClass> ?targetClass . }}
                OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetNode> ?targetNode . }}
                OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetSubjectsOf> ?targetSubjectsOf . }}
                OPTIONAL {{ ?nodeShape <http://www.w3.org/ns/shacl#targetObjectsOf> ?targetObjectsOf . }}
            }}
        """)
        shape_details_results = sparql.query().convert()

        shape_details_bindings = shape_details_results["results"]["bindings"]

        shape_details = {
            "Shape": shape_details_bindings[0].get("nodeShape", {}).get("value", "") if shape_details_bindings else "",
            "Type": "sh:NodeShape",
            "TargetClass": shape_details_bindings[0].get("targetClass", {}).get("value", "") if shape_details_bindings else "",
            "Properties": []
        }

        # Fetch all triples for the property shape
        sparql.setQuery(f"""
            SELECT ?predicate ?object
            FROM <{shapes_graph_uri}>
            WHERE {{
                <{source_shape}> ?predicate ?object .
            }}
        """)
        property_shape_results = sparql.query().convert()

        for triple in property_shape_results["results"]["bindings"]:
            predicate = triple["predicate"]["value"]
            obj = triple["object"]["value"]

            # Handle sh:in RDF list
            if predicate == "http://www.w3.org/ns/shacl#in" and (obj.startswith("nodeID://") or obj.startswith("_:")):
                obj = parse_rdf_list(obj, shapes_graph_uri)

            shape_details["Properties"].append({
                "Predicate": predicate,
                "Object": obj
            })

        # Construct violation entry
        violation_entry = {
            f"violation{idx}": {
                "full_validation_details": {
                    "FocusNode": focus_node,
                    "ResultPath": result_path,
                    "Value": value,
                    "Message": message,
                    "PropertyShape": source_shape,
                    "Severity": severity,
                    "TargetClass": shape_details["TargetClass"],
                    "TargetNode": shape_details_bindings[0].get("targetNode", {}).get("value", "") if shape_details_bindings else "",
                    "TargetSubjectsOf": shape_details_bindings[0].get("targetSubjectsOf", {}).get("value", "") if shape_details_bindings else "",
                    "TargetObjectsOf": shape_details_bindings[0].get("targetObjectsOf", {}).get("value", "") if shape_details_bindings else "",
                    "NodeShape": shape_details["Shape"],
                    "ConstraintComponent": constraint_component,
                },
                "shape_details": shape_details
            }
        }

        violations.append(violation_entry)

    # Final report
    report = {
        "@prefixes": prefixes,
        "violations": violations
    }

    return report


def get_most_violated_node_shape(shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> dict:
    """
    Find the Node Shape in the Shapes Graph with the highest number of violations.

    Args:
        shapes_graph_uri: The URI of the Shapes Graph.
        validation_report_uri: The URI of the Validation Report.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'nodeShape' (str): The URI of the most violated node shape.
            - 'violations' (int): The total number of violations for that shape.
    """

    # Step 1: Query Node Shapes and their associated Property Shapes
    query_shapes = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    SELECT DISTINCT ?nodeShape ?propertyShape
    FROM <{shapes_graph_uri}>
    WHERE {{
      ?nodeShape a sh:NodeShape ;
                 sh:property ?propertyShape .
    }}
    """
    response_shapes = requests.get(ENDPOINT_URL, params={"query": query_shapes, "format": "json"})
    response_shapes.raise_for_status()
    shapes_results = response_shapes.json()["results"]["bindings"]

    # Map Node Shapes to their Property Shapes
    node_shapes_map = {}
    for result in shapes_results:
        node_shape = result["nodeShape"]["value"]
        property_shape = result["propertyShape"]["value"]

        if node_shape not in node_shapes_map:
            node_shapes_map[node_shape] = []

        node_shapes_map[node_shape].append(property_shape)

    # Step 2: Query Violations for each Property Shape and aggregate by Node Shape
    node_shape_violations = {}
    for node_shape, property_shapes in node_shapes_map.items():
        total_violations = 0

        # Create a SPARQL VALUES clause for the Property Shapes
        property_shapes_values = " ".join([f"<{ps}>" for ps in property_shapes])

        query_violations = f"""
        SELECT (COUNT(*) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
          ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
          VALUES ?propertyShape {{ {property_shapes_values} }}
        }}
        """
        response_violations = requests.get(ENDPOINT_URL, params={"query": query_violations, "format": "json"})
        response_violations.raise_for_status()
        violations_results = response_violations.json()["results"]["bindings"]

        if violations_results:
            total_violations = int(violations_results[0]["violationCount"]["value"])

        node_shape_violations[node_shape] = total_violations

    # Step 3: Find the Node Shape with the highest number of violations
    most_violated_node_shape = max(node_shape_violations, key=node_shape_violations.get, default=None)
    max_violations = node_shape_violations[most_violated_node_shape] if most_violated_node_shape else 0
    
    return {
        "nodeShape": most_violated_node_shape,
        "violations": max_violations
    }


def get_most_violated_path(validation_report_uri: str = VALIDATION_REPORT_URI) -> dict:
    """
    Find the path in the validation report that caused the most violations.

    Args:
        validation_report_uri: The URI of the Validation Report. Default is VALIDATION_REPORT_URI.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'path' (str): The URI of the most violated path.
            - 'violations' (int): The violation count.
            
    Example:
        {'path': 'http://example.org/path', 'violations': 150}
    """

    # SPARQL query to find the most violated path
    query = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    SELECT ?path (COUNT(?violation) AS ?violationCount)
    FROM <{validation_report_uri}>
    WHERE {{
        ?violation sh:resultPath ?path .
      }}
    GROUP BY ?path
    ORDER BY DESC(?violationCount)
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
        most_violated_path = results[0]["path"]["value"]
        violation_count = int(results[0]["violationCount"]["value"])
        return {"path": most_violated_path, "violations": violation_count}
    else:
        return {"path": None, "violations": 0}


def get_most_violated_focus_node(validation_report_uri: str = VALIDATION_REPORT_URI) -> dict:
    """
    Find the focus node in the validation report that caused the most violations.

    Args:
        validation_report_uri (str): The URI of the Validation Report. Default is VALIDATION_REPORT_URI.

    Returns:
        dict: A dictionary containing the most violated focus node and its violation count, e.g.,
              {"focusNode": "http://example.org/node", "violations": 150}.
    """

    # SPARQL query to find the most violated focus node
    query = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    SELECT ?focusNode (COUNT(?violation) AS ?violationCount)
    FROM <{validation_report_uri}>
    WHERE {{
        ?violation sh:focusNode ?focusNode .
    }}
    GROUP BY ?focusNode
    ORDER BY DESC(?violationCount)
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
        most_violated_focus_node = results[0]["focusNode"]["value"]
        violation_count = int(results[0]["violationCount"]["value"])
        return {"focusNode": most_violated_focus_node, "violations": violation_count}
    else:
        return {"focusNode": None, "violations": 0}


def get_most_frequent_constraint_component(validation_report_uri: str = VALIDATION_REPORT_URI) -> dict:
    """
    Find the most frequent constraint component in the validation report.

    Args:
        validation_report_uri: The URI of the Validation Report. Default is VALIDATION_REPORT_URI.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'constraintComponent' (str): The URI of the most frequent constraint component.
            - 'occurrences' (int): The occurrence count.
            
    Example:
        {'constraintComponent': 'http://example.org/constraintComponent', 'occurrences': 250}
    """

    # SPARQL query to find the most frequent constraint component
    query = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    
    SELECT ?constraintComponent (COUNT(?violation) AS ?occurrenceCount)
    FROM <{validation_report_uri}>
    WHERE {{
        ?violation sh:sourceConstraintComponent ?constraintComponent .   
    }}
    GROUP BY ?constraintComponent
    ORDER BY DESC(?occurrenceCount)
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
        most_frequent_component = results[0]["constraintComponent"]["value"]
        occurrence_count = int(results[0]["occurrenceCount"]["value"])
        return {"constraintComponent": most_frequent_component, "occurrences": occurrence_count}
    else:
        return {"constraintComponent": None, "occurrences": 0}


def get_distinct_constraint_components_count(validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Find the number of distinct constraint components in the validation report.

    Args:
        validation_report_uri (str): The URI of the Validation Report. Default is VALIDATION_REPORT_URI.

    Returns:
        int: The total number of distinct constraint components.
    """

    # SPARQL query to count distinct constraint components
    query = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    SELECT (COUNT(DISTINCT ?constraintComponent) AS ?distinctCount)
    FROM <{validation_report_uri}> 
    WHERE {{
        ?violation sh:sourceConstraintComponent ?constraintComponent .
    }}
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
        distinct_count = int(results[0]["distinctCount"]["value"])
        return distinct_count
    else:
        return 0
    

def get_distinct_constraints_count_in_shapes(shapes_graph_uri: str = SHAPES_GRAPH_URI) -> int:
    """
    Count the number of distinct constraint types (from SHACL_FEATURES) used in the shapes graph.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is SHAPES_GRAPH_URI.

    Returns:
        int: The total number of distinct constraint types used in the shapes graph.
    """

    # Build the SPARQL VALUES clause with SHACL features
    shacl_features_values = " ".join([f"<{feature}>" for feature in SHACL_FEATURES])

    # SPARQL query to find distinct constraints in the shapes graph
    query = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    SELECT (COUNT(DISTINCT ?constraint) AS ?distinctCount)
    WHERE {{
      GRAPH <{shapes_graph_uri}> {{
        ?propertyShape ?constraint ?object .
        VALUES ?constraint {{ {shacl_features_values} }}
      }}
    }}
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
        distinct_count = int(results[0]["distinctCount"]["value"])
        return distinct_count
    else:
        return 0
