import subprocess
from SPARQLWrapper import SPARQLWrapper, JSON

# Global variables
ENDPOINT_URL = "http://localhost:8890/sparql"
SHAPES_GRAPH_URI = "http://ex.org/ShapesGraph"
VALIDATION_REPORT_URI = "http://ex.org/ValidationReport"

# ############ TODO to fix to use global variables #################

def load_graphs(directory: str, shapes_file: str, report_file: str):
    """
    Load two RDF files (ShapesGraph and ValidationReport) into Virtuoso using ISQL.

    Args:
        directory (str): Directory containing the RDF files.
        shapes_file (str): Name of the ShapesGraph file.
        report_file (str): Name of the ValidationReport file.

    Raises:
        TypeError: If any of the arguments are not strings.
        ValueError: If any of the arguments are empty strings.
    """
    
    # Type checking
    if not all(isinstance(arg, str) for arg in [directory, shapes_file, report_file]):
        raise TypeError("All arguments must be strings.")

    # Check for empty strings
    if not all(arg.strip() for arg in [directory, shapes_file, report_file]):
        raise ValueError("Arguments cannot be empty strings.")

    # Fixed ISQL configuration
    isql_port = "1111"
    username = "dba"
    password = "dba"

    
    # ISQL commands for both files
    isql_command = f"""
    ld_dir('{directory}', '{shapes_file}', 'http://ex.org/ShapesGraph');
    ld_dir('{directory}', '{report_file}', 'http://ex.org/ValidationReport');
    rdf_loader_run();

    """

    print("Executing ISQL command to load graphs...")

    try:
        # Execute ISQL command
        process = subprocess.run(
            ["isql", isql_port, username, password],
            input=isql_command,
            text=True,
            capture_output=True,
            check=True
        )

        print("ISQL command executed successfully!")
        print(process.stdout)

    except subprocess.CalledProcessError as e:
        print("ISQL command execution failed!")
        print(e.stderr)

    except FileNotFoundError:
        print("ISQL tool not found. Please check if Virtuoso is installed correctly.")



def get_all_shapes_names(graph_uri: str = "http://ex.org/ValidationReport") -> list:
    """
    Query the Virtuoso SPARQL endpoint to get all sh:sourceShape values
    from the specified graph.

    Args:
        graph_uri (str): The target graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list of shape names.
    """
    # Fixed SPARQL endpoint URL for Virtuoso
    endpoint_url = "http://localhost:8890/sparql"

    # Configure SPARQL query
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(f"""
        SELECT DISTINCT ?shape
        FROM <{graph_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> ?shape .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()
    shapes = [result["shape"]["value"] for result in results["results"]["bindings"]]

    return shapes



def get_all_focus_node_names(graph_uri: str = "http://ex.org/ValidationReport") -> list:
    """
    Query the Virtuoso SPARQL endpoint to get all sh:focusNode values
    from the specified graph.

    Args:
        graph_uri (str): The target graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list of focus node names.
    """
    # Fixed SPARQL endpoint URL for Virtuoso
    endpoint_url = "http://localhost:8890/sparql"

    # Configure SPARQL query
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(f"""
        SELECT DISTINCT ?focusNode
        FROM <{graph_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#focusNode> ?focusNode .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()
    focus_nodes = [result["focusNode"]["value"] for result in results["results"]["bindings"]]

    return focus_nodes



def get_all_property_path_names(graph_uri: str = "http://ex.org/ValidationReport") -> list:
    """
    Query the Virtuoso SPARQL endpoint to get all sh:resultPath values
    from the specified graph.

    Args:
        graph_uri (str): The target graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list of property path names.
    """
    # Fixed SPARQL endpoint URL for Virtuoso
    endpoint_url = "http://localhost:8890/sparql"

    # Configure SPARQL query
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyPath
        FROM <{graph_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#resultPath> ?propertyPath .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()
    property_paths = [result["propertyPath"]["value"] for result in results["results"]["bindings"]]

    return property_paths



def get_all_constraint_components_names(graph_uri: str = "http://ex.org/ValidationReport") -> list:
    """
    Query the Virtuoso SPARQL endpoint to get all sh:sourceConstraintComponent values
    from the specified graph.

    Args:
        graph_uri (str): The target graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list of constraint component names.
    """
    # Fixed SPARQL endpoint URL for Virtuoso
    endpoint_url = "http://localhost:8890/sparql"

    # Configure SPARQL query
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(f"""
        SELECT DISTINCT ?constraintComponent
        FROM <{graph_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
        }}
    """)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    results = sparql.query().convert()
    constraint_components = [result["constraintComponent"]["value"] for result in results["results"]["bindings"]]

    return constraint_components



def get_violations_for_shape_name(shape_name, graph_uri: str = "http://ex.org/ValidationReport") -> list:
    """
    Query the Virtuoso SPARQL endpoint to get all violations related to the specified property shape name.

    Args:
        shape_name (str or dict): The shape name (URI) as a string or a JSON object.
        graph_uri (str): The target graph URI to query. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list of violations with detailed information.
    """
    # Handle JSON input for shape_name
    if isinstance(shape_name, dict) and "shape" in shape_name:
        shape_name = shape_name["shape"]

    # Ensure the shape_name is a string
    if not isinstance(shape_name, str):
        raise ValueError("Invalid input: shape_name must be a string or a JSON object with a 'shape' key.")

    # Fixed SPARQL endpoint URL for Virtuoso
    endpoint_url = "http://localhost:8890/sparql"

    # Configure SPARQL query
    sparql = SPARQLWrapper(endpoint_url)
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



def get_number_of_shapes_in_shapes_graph(graph_uri: str = "http://ex.org/ShapesGraph") -> dict:
    """
    Query the Virtuoso SPARQL endpoint to get the number of Node Shapes and Property Shapes
    in the specified shapes graph, including blank nodes.

    Args:
        graph_uri (str): The target shapes graph URI to query. Default is "http://ex.org/ShapesGraph".

    Returns:
        dict: A JSON object containing the number of node shapes and property shapes.
    """
    # Fixed SPARQL endpoint URL for Virtuoso
    endpoint_url = "http://localhost:8890/sparql"

    # Configure SPARQL query to get the number of Node Shapes and Property Shapes (including blank nodes)
    sparql = SPARQLWrapper(endpoint_url)
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
    # Fixed SPARQL endpoint URL for Virtuoso
    endpoint_url = "http://localhost:8890/sparql"

    # Configure SPARQL query to count the number of sh:ValidationResult instances
    sparql = SPARQLWrapper(endpoint_url)
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



def map_property_shapes_to_node_shapes(validation_report_uri: str = "http://ex.org/ValidationReport",
                                       shapes_graph_uri: str = "http://ex.org/ShapesGraph") -> list:
    """
    Map property shapes from the validation report to their corresponding node shapes in the shapes graph.

    Args:
        validation_report_uri (str): The URI of the validation report graph. Default is "http://ex.org/ValidationReport".
        shapes_graph_uri (str): The URI of the shapes graph. Default is "http://ex.org/ShapesGraph".

    Returns:
        list: A JSON list of dictionaries mapping property shapes to node shapes.
    """
    # Fixed SPARQL endpoint URL for Virtuoso
    endpoint_url = "http://localhost:8890/sparql"

    # SPARQL query to get the mapping of property shapes to node shapes
    sparql = SPARQLWrapper(endpoint_url)
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




def get_shape_from_shapes_graph(node_shape_names: list) -> dict:
    """
    Query the Virtuoso SPARQL endpoint in two steps to avoid redundant triples:
    1. Query Node Shape triples.
    2. Query Property Shape triples for each Node Shape.

    Args:
        node_shape_names (list): A list of Node Shape URIs to query.

    Returns:
        dict: A JSON-like dictionary representing the Node Shape tree structure.
        
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
    # Fixed SPARQL endpoint URL and Shapes Graph URI
    endpoint_url = "http://localhost:8890/sparql"
    graph_uri = "http://ex.org/ShapesGraph"

    # Step 1: Query Node Shape triples
    node_shapes_values = " ".join([f"<{uri}>" for uri in node_shape_names])
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(f"""
        SELECT DISTINCT ?subject ?predicate ?object
        FROM <{graph_uri}>
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
            FROM <{graph_uri}>
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



# def get_number_of_violations_for_node_shape(nodeshape_name: str) -> int:
#     """
#     Query the Virtuoso SPARQL endpoint to get the number of violations related to the given Node Shape.

#     Args:
#         nodeshape_name (str): The URI of the Node Shape to query.

#     Returns:
#         int: The number of violations related to the Node Shape.
#     """
#     # Fixed SPARQL endpoint URLs and Graph URIs
#     endpoint_url = "http://localhost:8890/sparql"
#     shapes_graph_uri = "http://ex.org/ShapesGraph"
#     validation_report_uri = "http://ex.org/ValidationReport"

#     # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
#     sparql = SPARQLWrapper(endpoint_url)
#     sparql.setQuery(f"""
#         SELECT DISTINCT ?propertyShape
#         FROM <{shapes_graph_uri}>
#         WHERE {{
#             <{nodeshape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
#         }}
#     """)
#     sparql.setReturnFormat(JSON)
#     shapes_results = sparql.query().convert()

#     # Extract the list of Property Shapes
#     property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

#     # If no Property Shapes are found, return 0 violations
#     if not property_shapes:
#         return 0

#     # Prepare the list of Property Shapes as a SPARQL VALUES clause
#     property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

#     # Step 2: Query the Validation Report to count the number of violations for these Property Shapes
#     sparql.setQuery(f"""
#         SELECT (COUNT(?violation) AS ?violationCount)
#         FROM <{validation_report_uri}>
#         WHERE {{
#             ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
#             VALUES ?propertyShape {{ {property_shapes_values} }}
#         }}
#     """)
#     validation_results = sparql.query().convert()

#     # Extract the number of violations
#     violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])

#     return violation_count



# def get_number_of_property_paths_for_node_shape(shape_name: str) -> int:
#     """
#     Query the Virtuoso SPARQL endpoint to get the number of distinct sh:path values
#     for the given Node Shape from the Shapes Graph.

#     Args:
#         shape_name (str): The URI of the Node Shape to query.

#     Returns:
#         int: The number of distinct sh:path values for the Node Shape.
#     """
#     # Fixed SPARQL endpoint URL and Shapes Graph URI
#     endpoint_url = "http://localhost:8890/sparql"
#     graph_uri = "http://ex.org/ShapesGraph"

#     # SPARQL query to get the number of distinct sh:path values
#     sparql = SPARQLWrapper(endpoint_url)
#     sparql.setQuery(f"""
#         SELECT (COUNT(DISTINCT ?path) AS ?pathCount)
#         FROM <{graph_uri}>
#         WHERE {{
#             <{shape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
#             ?propertyShape <http://www.w3.org/ns/shacl#path> ?path .
#         }}
#     """)
#     sparql.setReturnFormat(JSON)

#     # Execute the query and process the results
#     results = sparql.query().convert()

#     # Extract the number of distinct paths
#     path_count = int(results["results"]["bindings"][0]["pathCount"]["value"])

#     return path_count



def get_number_of_property_shapes_for_node_shape(shape_name: str) -> int:
    """
    Query the Virtuoso SPARQL endpoint to get the number of Property Shapes
    associated with the given Node Shape from the Shapes Graph.

    Args:
        shape_name (str): The URI of the Node Shape to query.

    Returns:
        int: The number of Property Shapes associated with the Node Shape.
    """
    # Fixed SPARQL endpoint URL and Shapes Graph URI
    endpoint_url = "http://localhost:8890/sparql"
    graph_uri = "http://ex.org/ShapesGraph"

    # SPARQL query to count the number of Property Shapes
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?propertyShape) AS ?propertyShapeCount)
        FROM <{graph_uri}>
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



# def get_number_of_affected_focus_nodes_for_node_shape(nodeshape_name: str) -> int:
#     """
#     Query the Virtuoso SPARQL endpoint to get the number of unique sh:focusNode values
#     associated with the given Node Shape from the Validation Report.

#     Args:
#         nodeshape_name (str): The URI of the Node Shape to query.

#     Returns:
#         int: The number of unique sh:focusNode values associated with the Node Shape.
#     """
#     # Fixed SPARQL endpoint URLs and Graph URIs
#     endpoint_url = "http://localhost:8890/sparql"
#     shapes_graph_uri = "http://ex.org/ShapesGraph"
#     validation_report_uri = "http://ex.org/ValidationReport"

#     # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
#     sparql = SPARQLWrapper(endpoint_url)
#     sparql.setQuery(f"""
#         SELECT DISTINCT ?propertyShape
#         FROM <{shapes_graph_uri}>
#         WHERE {{
#             <{nodeshape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
#         }}
#     """)
#     sparql.setReturnFormat(JSON)
#     shapes_results = sparql.query().convert()

#     # Extract the list of Property Shapes
#     property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

#     # If no Property Shapes are found, return 0 affected focus nodes
#     if not property_shapes:
#         return 0

#     # Prepare the list of Property Shapes as a SPARQL VALUES clause
#     property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

#     # Step 2: Query the Validation Report to count the unique sh:focusNode values
#     sparql.setQuery(f"""
#         SELECT (COUNT(DISTINCT ?focusNode) AS ?focusNodeCount)
#         FROM <{validation_report_uri}>
#         WHERE {{
#             ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape ;
#                        <http://www.w3.org/ns/shacl#focusNode> ?focusNode .
#             VALUES ?propertyShape {{ {property_shapes_values} }}
#         }}
#     """)
#     validation_results = sparql.query().convert()

#     # Extract the number of unique focus nodes
#     focus_node_count = int(validation_results["results"]["bindings"][0]["focusNodeCount"]["value"])

#     return focus_node_count



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
    # Fixed SPARQL endpoint URLs and Graph URIs
    endpoint_url = "http://localhost:8890/sparql"
    shapes_graph_uri = "http://ex.org/ShapesGraph"
    validation_report_uri = "http://ex.org/ValidationReport"

    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
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
        FROM <{validation_report_uri}>
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




# def get_number_of_constraints_for_node_shape(nodeshape_name: str) -> int:
#     """
#     Query the Virtuoso SPARQL endpoint to get the number of unique constraints
#     (sh:sourceConstraintComponent) associated with the given Node Shape from the Validation Report.

#     Args:
#         nodeshape_name (str): The URI of the Node Shape to query.

#     Returns:
#         int: The number of unique constraints associated with the Node Shape.
#     """
#     # Fixed SPARQL endpoint URLs and Graph URIs
#     endpoint_url = "http://localhost:8890/sparql"
#     shapes_graph_uri = "http://ex.org/ShapesGraph"
#     validation_report_uri = "http://ex.org/ValidationReport"

#     # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
#     sparql = SPARQLWrapper(endpoint_url)
#     sparql.setQuery(f"""
#         SELECT DISTINCT ?propertyShape
#         FROM <{shapes_graph_uri}>
#         WHERE {{
#             <{nodeshape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
#         }}
#     """)
#     sparql.setReturnFormat(JSON)
#     shapes_results = sparql.query().convert()

#     # Extract the list of Property Shapes
#     property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

#     # If no Property Shapes are found, return 0 constraints
#     if not property_shapes:
#         return 0

#     # Prepare the list of Property Shapes as a SPARQL VALUES clause
#     property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

#     # Step 2: Query the Validation Report to count the unique constraints
#     sparql.setQuery(f"""
#         SELECT (COUNT(DISTINCT ?constraintComponent) AS ?constraintCount)
#         FROM <{validation_report_uri}>
#         WHERE {{
#             ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape ;
#                        <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
#             VALUES ?propertyShape {{ {property_shapes_values} }}
#         }}
#     """)
#     validation_results = sparql.query().convert()

#     # Extract the number of unique constraints
#     constraint_count = int(validation_results["results"]["bindings"][0]["constraintCount"]["value"])

#     return constraint_count


