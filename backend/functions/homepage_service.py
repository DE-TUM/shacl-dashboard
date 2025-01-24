from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from bs4 import BeautifulSoup

# Global variables
ENDPOINT_URL = "http://localhost:8890/sparql"
SHAPES_GRAPH_URI = "http://ex.org/ShapesGraph"
VALIDATION_REPORT_URI = "http://ex.org/ValidationReport"


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
            ?violation <http://www.w3.org/ns/shacl#focusNode> ?focusNode .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()

    # Extract the count of unique focus nodes
    focus_node_count = int(results["results"]["bindings"][0]["focusNodeCount"]["value"])

    return focus_node_count



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

