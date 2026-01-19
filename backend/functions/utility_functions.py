from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import os
from typing import List, Dict, Optional, Any
import logging
import time
import csv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI

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


def parse_rdf_list(node_id: str, shapes_graph_uri: str) -> List[str]:
    """
    Parse an RDF list given a node ID to extract the items in the list.

    Args:
        node_id (str): The node ID representing the RDF list.
        shapes_graph_uri (str): The URI of the Shapes Graph.

    Returns:
        List[str]: A list of item URIs in the RDF list.
    """
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT ?item
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_id}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> ?item ;
                        <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest>* ?restNode .
            FILTER(?restNode != <http://www.w3.org/1999/02/22-rdf-syntax-ns#nil>)
        }}
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Extract the items from the RDF list
    return [result["item"]["value"] for result in results["results"]["bindings"]]


def benchmark_function_execution(func: callable, runs: int = 10, csv_filename: str = "execution_time_use_case_1_lkg3_schema2.csv") -> Dict[str, Any]:
    """
    Measures the execution time of a function over multiple runs in milliseconds,
    and saves results to a CSV.

    Parameters:
        func (callable): The function to benchmark.
        runs (int): Number of times to run the function.
        csv_filename (str): Name of the CSV file to save results.

    Returns:
        dict: A dictionary with 'times_ms', 'average_ms', and 'results'.
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


def debug_check_data() -> None:
    """
    Debug function to check what data exists in Virtuoso.
    """
    sparql = SPARQLWrapper(ENDPOINT_URL)
    
    print("=== CHECKING VALIDATION REPORT GRAPH ===")
    
    # Check 1: Count all triples
    sparql.setQuery(f"""
        SELECT (COUNT(*) AS ?count)
        FROM <http://ex.org/ValidationReport>
        WHERE {{ ?s ?p ?o }}
    """)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()
    print(f"Total triples in ValidationReport: {result['results']['bindings'][0]['count']['value']}")
    
    # Check 2: Count ValidationResult instances
    sparql.setQuery(f"""
        SELECT (COUNT(?v) AS ?count)
        FROM <http://ex.org/ValidationReport>
        WHERE {{ ?v a <http://www.w3.org/ns/shacl#ValidationResult> }}
    """)
    result = sparql.query().convert()
    print(f"ValidationResult instances: {result['results']['bindings'][0]['count']['value']}")
    
    # Check 3: Sample violation data
    sparql.setQuery(f"""
        SELECT ?violation ?p ?o
        FROM <http://ex.org/ValidationReport>
        WHERE {{ 
            ?violation a <http://www.w3.org/ns/shacl#ValidationResult> .
            ?violation ?p ?o
        }}
        LIMIT 10
    """)
    result = sparql.query().convert()
    print(f"\nSample violation predicates:")
    for r in result['results']['bindings']:
        print(f"  {r['p']['value']}")
    
    print("\n=== CHECKING SHAPES GRAPH ===")
    
    # Check 4: Count NodeShapes
    sparql.setQuery(f"""
        SELECT (COUNT(?ns) AS ?count)
        FROM <http://ex.org/ShapesGraph>
        WHERE {{ ?ns a <http://www.w3.org/ns/shacl#NodeShape> }}
    """)
    result = sparql.query().convert()
    print(f"NodeShape instances: {result['results']['bindings'][0]['count']['value']}")
    
    # Check 5: Sample NodeShape with properties
    sparql.setQuery(f"""
        SELECT ?nodeShape ?propertyShape
        FROM <http://ex.org/ShapesGraph>
        WHERE {{ 
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                      <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
        LIMIT 5
    """)
    result = sparql.query().convert()
    print(f"\nSample NodeShapes with properties:")
    for r in result['results']['bindings']:
        print(f"  NodeShape: {r['nodeShape']['value']}")
        print(f"  PropertyShape: {r['propertyShape']['value']}")
