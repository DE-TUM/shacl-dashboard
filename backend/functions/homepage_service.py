from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import math
#from bs4 import BeautifulSoup
import time
import csv

"""
Homepage Service Module

This module provides functions for retrieving dashboard-level statistics and visualizations from 
SHACL validation reports and shapes graphs stored in a Virtuoso database.

The functions in this module query the validation report and shapes graph to provide:
1. Counts and basic statistics (violations, shapes, paths, etc.)
2. Distribution analysis for violations across different entities
3. Detailed validation reports with comprehensive information
4. Most violated entities identification

All functions accept customizable URIs for the validation report and shapes graph,
with sensible defaults defined as module-level constants.

Key functions:
- get_number_of_violations_in_validation_report: Count total violations
- get_number_of_node_shapes: Count node shapes in shapes graph
- get_number_of_node_shapes_with_violations: Count shapes with violations
- get_violations_per_node_shape: Get violations for each node shape
- distribution_of_violations_per_shape: Analyze violation distribution by shape
- generate_validation_details_report: Generate detailed validation reports
- get_most_violated_node_shape: Find the most violated node shape
"""


# Global variables
ENDPOINT_URL = "http://localhost:8890/sparql"
SHAPES_GRAPH_URI = "http://ex.org/ShapesGraph"
VALIDATION_REPORT_URI = "http://ex.org/ValidationReport"
SHACL_FEATURES = [
    "http://www.w3.org/ns/shacl#class",
    "http://www.w3.org/ns/shacl#datatype",
    "http://www.w3.org/ns/shacl#NodeKind",
    "http://www.w3.org/ns/shacl#minCount",
    "http://www.w3.org/ns/shacl#maxCount",
    "http://www.w3.org/ns/shacl#minExclusive",
    "http://www.w3.org/ns/shacl#minInclusive",
    "http://www.w3.org/ns/shacl#maxExclusive",
    "http://www.w3.org/ns/shacl#maxInclusive",
    "http://www.w3.org/ns/shacl#minLength",
    "http://www.w3.org/ns/shacl#maxLength",
    "http://www.w3.org/ns/shacl#pattern",
    "http://www.w3.org/ns/shacl#languageIn",
    "http://www.w3.org/ns/shacl#uniqueLang",
    "http://www.w3.org/ns/shacl#equals",
    "http://www.w3.org/ns/shacl#disjoint",
    "http://www.w3.org/ns/shacl#lessThan",
    "http://www.w3.org/ns/shacl#lessThanOrEquals",
    "http://www.w3.org/ns/shacl#not",
    "http://www.w3.org/ns/shacl#and",
    "http://www.w3.org/ns/shacl#or",
    "http://www.w3.org/ns/shacl#xone",
    "http://www.w3.org/ns/shacl#node",
    "http://www.w3.org/ns/shacl#qualifiedMinCount",
    "http://www.w3.org/ns/shacl#qualifiedMaxCount",
    "http://www.w3.org/ns/shacl#closed",
    "http://www.w3.org/ns/shacl#hasValue",
    "http://www.w3.org/ns/shacl#in"
]


def get_number_of_violations_in_validation_report(graph_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to get the total number of violations
    in the specified validation report graph.

    Args:
        graph_uri (str): The target validation report graph URI to query. Default is the global VALIDATION_REPORT_URI.

    Returns:
        int: The number of violations (sh:ValidationResult instances).
    """
    # Configure SPARQL query to count the number of sh:ValidationResult instances
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
    SELECT (COUNT(?violation) AS ?violationCount)
    FROM <{graph_uri}>
    WHERE {{
        ?report a <http://www.w3.org/ns/shacl#ValidationReport> ;
                <http://www.w3.org/ns/shacl#result> ?violation .
        ?violation a <http://www.w3.org/ns/shacl#ValidationResult> .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and process the results
        results = sparql.query().convert()

        # Extract the count from the results
        violation_count = int(results["results"]["bindings"][0]["violationCount"]["value"])

        return violation_count

    except Exception as e:
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
    # Configure SPARQL query to count Node Shapes
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?nodeShape) AS ?nodeShapesCount)
        FROM <{graph_uri}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the count from the results
    node_shapes_count = int(results["results"]["bindings"][0]["nodeShapesCount"]["value"])

    return node_shapes_count 


def get_number_of_node_shapes_with_violations(shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate how many Node Shapes in the Shapes Graph
    have at least one violation in the Validation Report.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of Node Shapes with violations.
    """
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?nodeShape) AS ?violatedNodeShapesCount)
        WHERE {{
            GRAPH <{shapes_graph_uri}> {{
                ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                           <http://www.w3.org/ns/shacl#property> ?propertyShape .
            }}
            GRAPH <{validation_report_uri}> {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
            }}
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the count from the results
    violated_node_shapes_count = int(results["results"]["bindings"][0]["violatedNodeShapesCount"]["value"])

    return violated_node_shapes_count


def get_number_of_paths_in_shapes_graph(graph_uri: str = SHAPES_GRAPH_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of unique paths (sh:path values)
    in the Shapes Graph.

    Args:
        graph_uri (str): The URI of the Shapes Graph to query. Default is "http://ex.org/ShapesGraph".

    Returns:
        int: The number of unique sh:path values in the Shapes Graph.
    """
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?path) AS ?pathCount)
        FROM <{graph_uri}>
        WHERE {{
            ?propertyShape <http://www.w3.org/ns/shacl#path> ?path .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the count of unique paths
    path_count = int(results["results"]["bindings"][0]["pathCount"]["value"])

    return path_count

def get_number_of_paths_with_violations(validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of unique paths (sh:resultPath values)
    in the Validation Report that caused violations.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of unique sh:resultPath values in the Validation Report.
    """
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?path) AS ?pathCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#resultPath> ?path .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the count of unique paths
    path_count = int(results["results"]["bindings"][0]["pathCount"]["value"])

    return path_count


def get_number_of_focus_nodes_in_validation_report(validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of unique sh:focusNode values
    in the Validation Report.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of unique sh:focusNode values in the Validation Report.
    """
    # Configure SPARQL query
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
    SELECT (COUNT(DISTINCT ?focusNode) AS ?focusNodeCount)
    FROM <{validation_report_uri}>
    WHERE {{
        ?report a <http://www.w3.org/ns/shacl#ValidationReport> ;
                <http://www.w3.org/ns/shacl#result> ?violation .

        ?violation a <http://www.w3.org/ns/shacl#ValidationResult> ;
                   <http://www.w3.org/ns/shacl#focusNode> ?focusNode .

        FILTER(isBlank(?violation))
    }}
""")

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the count of unique focus nodes
    focus_node_count = int(results["results"]["bindings"][0]["focusNodeCount"]["value"])

    return focus_node_count

print(get_number_of_violations_in_validation_report())
print(get_number_of_node_shapes_with_violations())
print(get_number_of_node_shapes())
print(get_number_of_focus_nodes_in_validation_report())
print(get_number_of_paths_with_violations())
print(get_number_of_paths_in_shapes_graph())

def count_triples(validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to count the number of triples in the Validation Report.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of triples in the Validation Report.
    """
    # Configure SPARQL query to count triples
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT (COUNT(*) AS ?tripleCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?s ?p ?o .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the count from the results
    triple_count = int(results["results"]["bindings"][0]["tripleCount"]["value"])

    return triple_count

print(count_triples())

def get_violations_per_node_shape(shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> list:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of violations for each Node Shape
    in the Shapes Graph, based on the associated Property Shapes in the Validation Report.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph to query. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list where each element contains a Node Shape name and its number of violations.
    """
    # Configure SPARQL query to get Node Shapes and their associated Property Shapes
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?nodeShape ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)
    shapes_results = sparql.query().convert()

    # Process Node Shapes and their Property Shapes
    node_shapes_map = {}
    for result in shapes_results["results"]["bindings"]:
        node_shape = result["nodeShape"]["value"]
        property_shape = result["propertyShape"]["value"]
        if node_shape not in node_shapes_map:
            node_shapes_map[node_shape] = []
        node_shapes_map[node_shape].append(property_shape)

    # Initialize list to store the final result
    violations_per_node_shape = []

    # For each Node Shape, calculate the number of violations
    for node_shape, property_shapes in node_shapes_map.items():
        property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])
        sparql.setQuery(f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{validation_report_uri}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
                VALUES ?propertyShape {{ {property_shapes_values} }}
            }}
        """)
        validation_results = sparql.query().convert()

        # Extract the violation count for the current Node Shape
        violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])

        # Append the result to the list
        violations_per_node_shape.append({
            "NodeShapeName": node_shape,
            "NumViolations": violation_count
        })

    return violations_per_node_shape


def get_violations_per_path(validation_report_uri: str = VALIDATION_REPORT_URI) -> list:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of violations for each unique sh:resultPath
    in the Validation Report.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list where each element contains a result path name and its number of violations.
    """
    # Configure SPARQL query to count violations per result path
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT ?path (COUNT(?violation) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#resultPath> ?path .
        }}
        GROUP BY ?path
        ORDER BY DESC(?violationCount)
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Build the JSON list from the results
    violations_per_path = [
        {
            "PathName": result["path"]["value"],
            "NumViolations": int(result["violationCount"]["value"])
        }
        for result in results["results"]["bindings"]
    ]

    return violations_per_path



def get_violations_per_focus_node(validation_report_uri: str = VALIDATION_REPORT_URI) -> list:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of violations for each unique sh:focusNode
    in the Validation Report.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list where each element contains a focus node name and its number of violations.
    """
    # Configure SPARQL query to count violations per focus node
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT ?focusNode (COUNT(?violation) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#focusNode> ?focusNode .
        }}
        GROUP BY ?focusNode
        ORDER BY DESC(?violationCount)
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Build the JSON list from the results
    violations_per_focus_node = [
        {
            "FocusNodeName": result["focusNode"]["value"],
            "NumViolations": int(result["violationCount"]["value"])
        }
        for result in results["results"]["bindings"]
    ]

    return violations_per_focus_node

def distribution_of_violations_per_shape(
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI
) -> dict:
    """
    Prepare data for a bar chart showing the frequency of Node Shapes in different violation ranges.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph to query. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        dict: A dictionary formatted for bar chart visualization with labels and datasets.
    """
    # Step 1: Get the violation data for each Node Shape
    violations_data = get_violations_per_node_shape(shapes_graph_uri, validation_report_uri)

    # Step 2: Extract the maximum number of violations
    max_violations = max([item["NumViolations"] for item in violations_data])

    # Step 3: Calculate the range size and labels
    num_bins = 10  # Number of bins (bars) for the chart
    bin_size = max(1, (max_violations // num_bins) + (1 if max_violations % num_bins else 0))  # Ensure at least size 1
    labels = [f"{i}-{i + bin_size - 1}" for i in range(0, bin_size * num_bins, bin_size)]

    # Step 4: Initialize frequency counts for each bin
    frequencies = [0] * num_bins

    # Step 5: Count the number of Node Shapes in each bin
    for item in violations_data:
        num_violations = item["NumViolations"]
        bin_index = min(num_violations // bin_size, num_bins - 1)  # Ensure the last bin includes the max value
        frequencies[bin_index] += 1

    # Step 6: Prepare the final data format for the bar chart
    bar_chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Frequency",
                "data": frequencies,
            }
        ],
    }

    return bar_chart_data


def distribution_of_violations_per_path(validation_report_uri: str = VALIDATION_REPORT_URI) -> dict:
    """
    Prepare data for a bar chart showing the distribution of violations per unique sh:resultPath
    in the Validation Report, grouped by violation count ranges.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        dict: A dictionary formatted for bar chart visualization with labels and datasets.
    """
    # Step 1: Get the violations data for each path
    violations_data = get_violations_per_path(validation_report_uri)

    # Step 2: Extract the maximum number of violations
    max_violations = max([item["NumViolations"] for item in violations_data]) if violations_data else 0

    # Step 3: Calculate the range size and labels
    num_bins = 10  # Number of bins (bars) for the chart
    bin_size = max(1, (max_violations // num_bins) + (1 if max_violations % num_bins else 0))  # Ensure at least size 1
    labels = [f"{i}-{i + bin_size - 1}" for i in range(0, bin_size * num_bins, bin_size)]

    # Step 4: Initialize frequency counts for each bin
    frequencies = [0] * num_bins

    # Step 5: Count the number of paths in each bin
    for item in violations_data:
        num_violations = item["NumViolations"]
        bin_index = min(num_violations // bin_size, num_bins - 1)  # Ensure the last bin includes the max value
        frequencies[bin_index] += 1

    # Step 6: Prepare the final data format for the bar chart
    bar_chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Number of Paths",
                "data": frequencies,
            }
        ],
    }

    return bar_chart_data


def distribution_of_violations_per_focus_node(validation_report_uri: str = VALIDATION_REPORT_URI) -> dict:
    """
    Prepare data for a bar chart showing the distribution of violations per unique sh:focusNode
    in the Validation Report, grouped by violation count ranges.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        dict: A dictionary formatted for bar chart visualization with labels and datasets.
    """
    # Step 1: Get the violations data for each focus node
    violations_data = get_violations_per_focus_node(validation_report_uri)

    # Step 2: Extract the maximum number of violations
    max_violations = max([item["NumViolations"] for item in violations_data]) if violations_data else 0

    # Step 3: Calculate the range size and labels
    num_bins = 10  # Number of bins (bars) for the chart
    bin_size = max(1, (max_violations // num_bins) + (1 if max_violations % num_bins else 0))  # Ensure at least size 1
    labels = [f"{i}-{i + bin_size - 1}" for i in range(0, bin_size * num_bins, bin_size)]

    # Step 4: Initialize frequency counts for each bin
    frequencies = [0] * num_bins

    # Step 5: Count the number of focus nodes in each bin
    for item in violations_data:
        num_violations = item["NumViolations"]
        bin_index = min(num_violations // bin_size, num_bins - 1)  # Ensure the last bin includes the max value
        frequencies[bin_index] += 1

    # Step 6: Prepare the final data format for the bar chart
    bar_chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Number of Focus Nodes",
                "data": frequencies,
            }
        ],
    }

    return bar_chart_data



def get_prefixes_from_endpoint(endpoint_url: str) -> dict:
    """
    Retrieve prefixes defined in the SPARQL endpoint using the `nsdecl` query.

    Args:
        endpoint_url (str): The base URL of the SPARQL endpoint (e.g., http://localhost:8890).

    Returns:
        dict: A dictionary of prefixes and their namespaces.
    """
    try:
        # Construct the nsdecl URL
        nsdecl_url = f"{endpoint_url}?help=nsdecl"
        
        # Send an HTTP GET request
        response = requests.get(nsdecl_url)
        response.raise_for_status()  # Raise an error for HTTP issues

        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract prefixes and namespaces
        prefixes = {}
        table = soup.find("table")  # Assume prefixes are listed in an HTML table
        if table:
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip the header row
                cells = row.find_all("td")
                if len(cells) == 2:
                    prefix = cells[0].text.strip()
                    namespace = cells[1].text.strip()
                    prefixes[prefix] = namespace
        else:
            # Handle plain text response
            for line in response.text.splitlines():
                if line.strip() and "\t" in line:  # Assume tab-separated prefix-namespace pairs
                    prefix, namespace = line.split("\t", 1)
                    prefixes[prefix.strip()] = namespace.strip()

        return prefixes

    except Exception as e:
        print(f"Error fetching prefixes from SPARQL endpoint: {e}")
        return {}


def parse_rdf_list(node_id: str, shapes_graph_uri: str) -> list:
    """
    Parse an RDF list given a node ID to extract the items in the list.

    Args:
        node_id (str): The node ID representing the RDF list.
        shapes_graph_uri (str): The URI of the Shapes Graph.

    Returns:
        list: A list of items in the RDF list.
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


def generate_validation_details_report(
    validation_report_uri: str = VALIDATION_REPORT_URI,
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    limit: int = 10,
    offset: int = 0
) -> dict:
    """
    Generate a detailed validation report with prefixes, violations, and shape details.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query.
        shapes_graph_uri (str): The URI of the Shapes Graph to query.
        limit (int): Maximum number of violations to return. Default is 10.
        offset (int): Offset for the violations to return. Default is 0.

    Returns:
        dict: A dictionary containing prefixes and a detailed list of violations.
    """
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
        shapes_graph_uri (str): The URI of the Shapes Graph.
        validation_report_uri (str): The URI of the Validation Report.

    Returns:
        dict: A dictionary containing the name of the Node Shape and its total number of violations.
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
        validation_report_uri (str): The URI of the Validation Report. Default is VALIDATION_REPORT_URI.

    Returns:
        dict: A dictionary containing the most violated path and its violation count, e.g.,
              {"path": "http://example.org/path", "violations": 150}.
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
        validation_report_uri (str): The URI of the Validation Report. Default is VALIDATION_REPORT_URI.

    Returns:
        dict: A dictionary containing the most frequent constraint component and its occurrence count, e.g.,
              {"constraintComponent": "http://example.org/constraintComponent", "occurrences": 250}.
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

print(get_distinct_constraints_count_in_shapes())

def get_distribution_of_violations_per_constraint_component(
    validation_report_uri: str = VALIDATION_REPORT_URI,
) -> dict:
    """
    Generate data for a bar chart representing the distribution of violations per constraint component.

    Args:
        validation_report_uri (str): The URI of the Validation Report. Default is VALIDATION_REPORT_URI.

    Returns:
        dict: A dictionary formatted for a bar chart, e.g.,
        {
            "labels": ["0-10", "11-20", ...],
            "datasets": [
                {
                    "label": "Number of Constraint Components",
                    "data": [5, 12, ...],
                }
            ],
        }
    """
    num_bins = 10  # Fixed number of bins

    # SPARQL query to get violation counts per constraint component
    query = f"""
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    SELECT ?constraintComponent (COUNT(?violation) AS ?violationCount)
    WHERE {{
      GRAPH <{validation_report_uri}> {{
        ?violation sh:sourceConstraintComponent ?constraintComponent .
      }}
    }}
    GROUP BY ?constraintComponent
    """
    
    # Execute the query
    response = requests.get(
        ENDPOINT_URL,
        params={"query": query, "format": "json"},
    )
    response.raise_for_status()
    results = response.json()["results"]["bindings"]

    # Extract violation counts for each constraint component
    violation_counts = [int(row["violationCount"]["value"]) for row in results]

    # Determine bin size and labels
    if not violation_counts:
        # No data to process
        return {
            "labels": [f"0-{num_bins}"] * num_bins,
            "datasets": [{"label": "Number of Constraint Components", "data": [0] * num_bins}],
        }

    max_value = max(violation_counts)
    bin_size = math.ceil(max_value / num_bins)

    # Generate labels for bins
    labels = [f"{i}-{i + bin_size - 1}" for i in range(0, bin_size * num_bins, bin_size)]

    # Calculate frequencies for each bin
    frequencies = [0] * num_bins
    for count in violation_counts:
        bin_index = min(count // bin_size, num_bins - 1)
        frequencies[bin_index] += 1

    # Prepare the bar chart data
    bar_chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Number of Constraint Components",
                "data": frequencies,
            }
        ],
    }

    return bar_chart_data

print(get_distribution_of_violations_per_constraint_component())

def distribution_of_violations_per_path_with_adaptive_bins(validation_report_uri: str = VALIDATION_REPORT_URI) -> dict:
    """
    Prepare data for a bar chart showing the distribution of violations per unique sh:resultPath
    in the Validation Report, grouped by adaptive violation count ranges.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        dict: A dictionary formatted for bar chart visualization with labels and datasets.
    """
    # Step 1: Get the violations data for each path
    violations_data = get_violations_per_path(validation_report_uri)

    # Step 2: Extract the violation counts
    violation_counts = sorted([item["NumViolations"] for item in violations_data]) if violations_data else []

    if not violation_counts:
        return {"labels": [], "datasets": [{"label": "Number of Paths", "data": []}]}

    # Step 3: Define adaptive bins
    bins = [0, 10, 50, 100, 500, 1000, 5000, 10000, 20000, max(violation_counts) + 1]
    labels = [f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins) - 1)]

    # Step 4: Initialize frequency counts for each bin
    frequencies = [0] * (len(bins) - 1)

    # Step 5: Count the number of paths in each bin
    for count in violation_counts:
        for i in range(len(bins) - 1):
            if bins[i] <= count < bins[i + 1]:
                frequencies[i] += 1
                break

    # Step 6: Prepare the final data format for the bar chart
    bar_chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Number of Paths",
                "data": frequencies,
            }
        ],
    }

    return bar_chart_data

def benchmark_function_execution(func, runs=10, csv_filename="execution_time_use_case_1_lkg3_schema2.csv"):
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
print(get_most_violated_node_shape())
# Execution Use Case 1    
benchmark_function_execution(get_most_violated_node_shape)