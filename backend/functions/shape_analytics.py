import sys
import os
from typing import List, Dict, Any, Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI, SHACL_FEATURES
import math
import requests
import logging

logger = logging.getLogger(__name__)

"""
Shape Analytics Module

This module provides advanced analytics functions for analyzing shapes,
including distribution of violations, entropy calculations, correlation
analysis, and detailed node shape tables.

Key functions:
- get_distribution_of_violations_per_constraint: Generate violation distribution data
- calculate_shannon_entropy: Calculate Shannon entropy for violation distributions
- get_correlation_of_constraints_and_violations: Analyze correlation between constraints and violations
- get_node_shape_details_table: Generate detailed table of node shape information
"""


def get_distribution_of_violations_per_constraint(
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI,
    num_bins: int = 10,
) -> Dict[str, Any]:
    """
    Generate data for the "Distribution of Violations per Constraint" plot in a single SPARQL query.

    This function calculates the ratio of violations to constraints for each Node Shape
    and creates a frequency distribution binned into the specified number of bins.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph to query.
        validation_report_uri (str): The URI of the Validation Report to query.
        num_bins (int): Number of bins for the plot. Default is 10.

    Returns:
        Dict[str, Any]: A dictionary containing 'labels' (list of bin ranges) and 
            'datasets' (list with frequency data for the plot).

    Example:
        >>> result = get_distribution_of_violations_per_constraint(num_bins=5)
        >>> print(result['labels'])  # ['0-19', '20-39', '40-59', '60-79', '80-99']
        >>> print(result['datasets'][0]['data'])  # [5, 10, 3, 2, 0]
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
    """
    Calculate the Shannon entropy of a distribution of violation counts.

    Args:
        violation_counts (Dict[str, int]): Dictionary mapping constraint components to their violation counts.

    Returns:
        float: The Shannon entropy value.
    """
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
