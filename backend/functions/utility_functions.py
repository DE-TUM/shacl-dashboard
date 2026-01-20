import sys
import os
from typing import List, Dict, Optional, Any
import logging
import time
import csv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SHAPES_GRAPH_URI, VALIDATION_REPORT_URI
from sparql_executor import SparqlQueryExecutor, get_default_executor

logger = logging.getLogger(__name__)

"""
Utility Functions Module

This module provides utility functions for working with SHACL validation reports and shapes graphs,
including prefix extraction, RDF list parsing, benchmarking, and debugging utilities.

Key functions:
- get_prefixes_from_endpoint: Extract namespace prefixes from SPARQL endpoint
- parse_rdf_list: Parse RDF lists to extract their items
- benchmark_function_execution: Measure and log function execution times
- debug_check_data: Debug utility to inspect Virtuoso data
"""


def get_prefixes_from_endpoint(endpoint_url: str) -> Dict[str, str]:
    """
    Retrieve prefixes by discovering URIs from Virtuoso SPARQL endpoint.
    Extracts namespaces from actual data in the database.

    Args:
        endpoint_url (str): The base URL of the SPARQL endpoint (e.g., http://localhost:8890/sparql).

    Returns:
        Dict[str, str]: A dictionary mapping prefix names to their namespace URIs.
    """
    from .prefix_utils import extract_prefixes_from_sparql_graphs
    
    # Always extract prefixes from what's actually in Virtuoso
    try:
        prefixes = extract_prefixes_from_sparql_graphs(
            endpoint_url,
            [SHAPES_GRAPH_URI, VALIDATION_REPORT_URI]
        )
        return prefixes
    except Exception as e:
        print(f"⚠️  Error extracting prefixes from SPARQL endpoint: {e}")
    
    # Minimal fallback only if extraction completely fails
    return {
        'sh': 'http://www.w3.org/ns/shacl#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'shs': 'http://shaclshapes.org/',
    }


def parse_rdf_list(node_id: str, shapes_graph_uri: str, executor: Optional[SparqlQueryExecutor] = None) -> List[str]:
    """
    Parse an RDF list (rdf:List) to extract all items in sequential order.

    This function traverses an RDF list structure using rdf:first and rdf:rest predicates
    to extract all items. RDF lists are commonly used in SHACL for sh:in constraints.

    Args:
        node_id (str): The node ID or blank node representing the RDF list head 
            (e.g., "nodeID://b12345" or "_:b12345").
        shapes_graph_uri (str): The URI of the Shapes Graph containing the RDF list.
        executor (Optional[SparqlQueryExecutor]): Optional executor instance. Uses default if not provided.

    Returns:
        List[str]: A list of item URIs in the order they appear in the RDF list.

    Example:
        >>> # For sh:in with values ["red", "green", "blue"]
        >>> items = parse_rdf_list("nodeID://b12345", "http://ex.org/shapes")
        >>> print(items)
        ['red', 'green', 'blue']
    """
    if executor is None:
        executor = get_default_executor()
    
    query = f"""
        SELECT ?item
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_id}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> ?item ;
                        <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest>* ?restNode .
            FILTER(?restNode != <http://www.w3.org/1999/02/22-rdf-syntax-ns#nil>)
        }}
    """
    
    results = executor.execute_query(query, shapes_graph_uri, "parse_rdf_list")

    # Extract the items from the RDF list
    return [result["item"]["value"] for result in results["results"]["bindings"]]


def benchmark_function_execution(func: callable, runs: int = 10, csv_filename: str = "execution_time_use_case_1_lkg3_schema2.csv") -> Dict[str, Any]:
    """
    Measures the execution time of a function over multiple runs in milliseconds,
    and saves results to a CSV file.

    This function executes the provided function multiple times, measures each execution
    time, calculates the average, and exports all results to a CSV file for analysis.

    Args:
        func (callable): The function to benchmark. Should be a no-argument function.
        runs (int): Number of times to run the function. Default is 10.
        csv_filename (str): Name of the CSV file to save results. Default is
            "execution_time_use_case_1_lkg3_schema2.csv".

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'times_ms': List of execution times in milliseconds for each run
            - 'average_ms': Average execution time across all runs
            - 'results': List of return values from each function execution

    Example:
        >>> def my_query():
        ...     return get_number_of_violations_in_validation_report()
        >>> stats = benchmark_function_execution(my_query, runs=5, csv_filename="query_perf.csv")
        >>> print(f"Average time: {stats['average_ms']:.2f}ms")
        Average time: 245.67ms
    """
    execution_times_ms = []
    results = []

    for i in range(runs):
        start_time = time.time()
        result = func()
        end_time = time.time()

        elapsed_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        execution_times_ms.append(elapsed_ms)
        results.append(result)
        print(f"Run {i+1}: {elapsed_ms:.2f} ms")

    average_ms = sum(execution_times_ms) / runs
    print(f"\nAverage execution time: {average_ms:.2f} ms")

    # Save to CSV
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Run", "Execution Time (ms)"])
        for idx, t in enumerate(execution_times_ms, start=1):
            writer.writerow([idx, t])
        writer.writerow(["Average", average_ms])

    print(f"\nAll execution times and average saved to '{csv_filename}'")

    return {
        "times_ms": execution_times_ms,
        "average_ms": average_ms,
        "results": results
    }


def debug_check_data(executor: Optional[SparqlQueryExecutor] = None) -> None:
    """
    Debug function to check what data exists in Virtuoso.
    
    Args:
        executor (Optional[SparqlQueryExecutor]): Optional executor instance.
    """
    if executor is None:
        executor = get_default_executor()
    
    print("=== CHECKING VALIDATION REPORT GRAPH ===")
    
    # Check 1: Count all triples
    query = f"""
        SELECT (COUNT(*) AS ?count)
        FROM <http://ex.org/ValidationReport>
        WHERE {{ ?s ?p ?o }}
    """
    result = executor.execute_query(query, "http://ex.org/ValidationReport", "debug_count_all_triples")
    print(f"Total triples in ValidationReport: {result['results']['bindings'][0]['count']['value']}")
    
    # Check 2: Count ValidationResult instances
    query = f"""
        SELECT (COUNT(?v) AS ?count)
        FROM <http://ex.org/ValidationReport>
        WHERE {{ ?v a <http://www.w3.org/ns/shacl#ValidationResult> }}
    """
    result = executor.execute_query(query, "http://ex.org/ValidationReport", "debug_count_validation_results")
    print(f"ValidationResult instances: {result['results']['bindings'][0]['count']['value']}")
    
    # Check 3: Sample violation data
    query = f"""
        SELECT ?violation ?p ?o
        FROM <http://ex.org/ValidationReport>
        WHERE {{ 
            ?violation a <http://www.w3.org/ns/shacl#ValidationResult> .
            ?violation ?p ?o
        }}
        LIMIT 10
    """
    result = executor.execute_query(query, "http://ex.org/ValidationReport", "debug_sample_violations")
    print(f"\nSample violation predicates:")
    for r in result['results']['bindings']:
        print(f"  {r['p']['value']}")
    
    print("\n=== CHECKING SHAPES GRAPH ===")
    
    # Check 4: Count NodeShapes
    query = f"""
        SELECT (COUNT(?ns) AS ?count)
        FROM <http://ex.org/ShapesGraph>
        WHERE {{ ?ns a <http://www.w3.org/ns/shacl#NodeShape> }}
    """
    result = executor.execute_query(query, "http://ex.org/ShapesGraph", "debug_count_node_shapes")
    print(f"NodeShape instances: {result['results']['bindings'][0]['count']['value']}")
    
    # Check 5: Sample NodeShape with properties
    query = f"""
        SELECT ?nodeShape ?propertyShape
        FROM <http://ex.org/ShapesGraph>
        WHERE {{ 
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                      <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
        LIMIT 5
    """
    result = executor.execute_query(query, "http://ex.org/ShapesGraph", "debug_sample_node_shapes")
    print(f"\nSample NodeShapes with properties:")
    for r in result['results']['bindings']:
        print(f"  NodeShape: {r['nodeShape']['value']}")
        print(f"  PropertyShape: {r['propertyShape']['value']}")
