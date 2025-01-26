from SPARQLWrapper import SPARQLWrapper, JSON
import math
import requests

# Global variables
ENDPOINT_URL = "http://localhost:8890/sparql"
SHAPES_GRAPH_URI = "http://ex.org/ShapesGraph"
VALIDATION_REPORT_URI = "http://ex.org/ValidationReport"

# Define the set of SHACL features to check for constraints using full URIs
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


def get_number_of_violations_for_node_shape(nodeshape_name: str, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of violations related to the given Node Shape.

    Args:
        nodeshape_name (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of violations related to the Node Shape.
    """
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{nodeshape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)
    shapes_results = sparql.query().convert()

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return 0 violations
    if not property_shapes:
        return 0

    # Prepare the list of Property Shapes as a SPARQL VALUES clause
    property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

    # Step 2: Query the Validation Report to count the number of violations for these Property Shapes
    sparql.setQuery(f"""
        SELECT (COUNT(?violation) AS ?violationCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
            VALUES ?propertyShape {{ {property_shapes_values} }}
        }}
    """)
    validation_results = sparql.query().convert()

    # Extract the number of violations
    violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])

    return violation_count



def get_number_of_violated_focus_for_node_shape(node_shape: str, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of unique sh:focusNode values
    in the Validation Report that are violated due to the given Node Shape.

    Args:
        node_shape (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of unique sh:focusNode values related to violations caused by the Node Shape.
    """
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)
    shapes_results = sparql.query().convert()

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return 0 focus nodes
    if not property_shapes:
        return 0

    # Prepare the list of Property Shapes as a SPARQL VALUES clause
    property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

    # Step 2: Query the Validation Report to count unique focus nodes for these Property Shapes
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?focusNode) AS ?focusNodeCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape ;
                       <http://www.w3.org/ns/shacl#focusNode> ?focusNode .
            VALUES ?propertyShape {{ {property_shapes_values} }}
        }}
    """)
    validation_results = sparql.query().convert()

    # Extract the count of unique focus nodes
    focus_node_count = int(validation_results["results"]["bindings"][0]["focusNodeCount"]["value"])

    return focus_node_count



def get_number_of_property_paths_for_node_shape(shape_name: str, shapes_graph_uri: str = SHAPES_GRAPH_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to calculate the number of unique sh:path values
    for the given Node Shape in the Shapes Graph.

    Args:
        shape_name (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".

    Returns:
        int: The number of unique sh:path values for the Node Shape.
    """
    # Configure SPARQL query to count unique paths
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?path) AS ?pathCount)
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{shape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
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



def get_number_of_constraints_for_node_shape(node_shape_name: str, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> int:
    """
    Query the Virtuoso SPARQL endpoint to get the number of unique constraints
    (sh:sourceConstraintComponent) associated with the given Node Shape from the Validation Report.

    Args:
        node_shape_name (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        int: The number of unique constraints associated with the Node Shape.
    """
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)

    try:
        shapes_results = sparql.query().convert()
    except Exception as e:
        raise RuntimeError(f"Error querying Shapes Graph: {str(e)}")

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return 0 constraints
    if not property_shapes:
        return 0

    # Prepare the list of Property Shapes as a SPARQL VALUES clause
    property_shapes_values = " ".join([f"<{uri}>" for uri in property_shapes])

    # Step 2: Query the Validation Report to count the unique constraints
    sparql.setQuery(f"""
        SELECT (COUNT(DISTINCT ?constraintComponent) AS ?constraintCount)
        FROM <{validation_report_uri}>
        WHERE {{
            ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape ;
                       <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
            VALUES ?propertyShape {{ {property_shapes_values} }}
        }}
    """)
    try:
        validation_results = sparql.query().convert()
    except Exception as e:
        raise RuntimeError(f"Error querying Validation Report: {str(e)}")

    # Extract the number of unique constraints
    constraint_count = int(validation_results["results"]["bindings"][0]["constraintCount"]["value"])

    return constraint_count



def get_property_shapes(node_shape: str, limit: int = None, offset: int = None, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> list:
    """
    Retrieve Property Shapes associated with the given Node Shape, including statistics about violations,
    constraints, and the most violated constraint.

    Args:
        node_shape (str): The URI of the Node Shape to query.
        limit (int, optional): Maximum number of Property Shapes to return. Default is None (no limit).
        offset (int, optional): Offset for the Property Shapes to return. Default is None (no offset).
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list of Property Shapes with their statistics.
    """
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape

    # Build the SPARQL query with optional LIMIT and OFFSET
    query = f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """
    if limit is not None:
        query += f" LIMIT {limit}"
    if offset is not None:
        query += f" OFFSET {offset}"

    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        shapes_results = sparql.query().convert()
    except Exception as e:
        raise RuntimeError(f"Error querying Shapes Graph: {str(e)}")

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return an empty list
    if not property_shapes:
        return []

    # Initialize list to store the final result
    property_shapes_info = []

    # Step 2: For each Property Shape, calculate statistics
    for property_shape in property_shapes:
        # Query the number of violations for the Property Shape
        sparql.setQuery(f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{validation_report_uri}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> .
            }}
        """)
        violation_results = sparql.query().convert()
        num_violations = int(violation_results["results"]["bindings"][0]["violationCount"]["value"])

        if num_violations == 0:
            # If no violations, append default values and skip further checks
            property_shapes_info.append({
                "PropertyShapeName": property_shape,
                "NumViolations": 0,
                "NumConstraints": 0,
                "MostViolatedConstraint": None,
            })
        else:
            # Query the number of unique constraints for the Property Shape
            sparql.setQuery(f"""
                SELECT (COUNT(DISTINCT ?constraintComponent) AS ?constraintCount)
                FROM <{validation_report_uri}>
                WHERE {{
                    ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                            <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
                }}
            """)
            constraint_results = sparql.query().convert()
            num_constraints = int(constraint_results["results"]["bindings"][0]["constraintCount"]["value"])

            # Query the most violated constraint for the Property Shape
            sparql.setQuery(f"""
                SELECT ?constraintComponent (COUNT(?violation) AS ?violationCount)
                FROM <{validation_report_uri}>
                WHERE {{
                    ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                            <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
                }}
                GROUP BY ?constraintComponent
                ORDER BY DESC(?violationCount)
                LIMIT 1
            """)
            most_violated_results = sparql.query().convert()
            most_violated_constraint = (
                most_violated_results["results"]["bindings"][0]["constraintComponent"]["value"]
                if most_violated_results["results"]["bindings"] else None
            )

            # Append statistics for the current Property Shape
            property_shapes_info.append({
                "PropertyShapeName": property_shape,
                "NumViolations": num_violations,
                "NumConstraints": num_constraints,
                "MostViolatedConstraint": most_violated_constraint,
            })

    return property_shapes_info


def get_number_of_violations_per_constraint_type_for_property_shape(node_shape: str, shapes_graph_uri: str = SHAPES_GRAPH_URI, validation_report_uri: str = VALIDATION_REPORT_URI) -> list:
    """
    Retrieve the number of violations per constraint type (sh:sourceConstraintComponent) for each
    Property Shape associated with the given Node Shape.

    Args:
        node_shape (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report. Default is "http://ex.org/ValidationReport".

    Returns:
        list: A JSON list of Property Shapes with their violations categorized by constraints.
    """
    # Step 1: Query the Shapes Graph to get the Property Shapes associated with the Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?propertyShape
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{node_shape}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)

    try:
        shapes_results = sparql.query().convert()
    except Exception as e:
        raise RuntimeError(f"Error querying Shapes Graph: {str(e)}")

    # Extract the list of Property Shapes
    property_shapes = [result["propertyShape"]["value"] for result in shapes_results["results"]["bindings"]]

    # If no Property Shapes are found, return an empty list
    if not property_shapes:
        return []

    # Initialize list to store the final result
    property_shapes_info = []

    # Step 2: For each Property Shape, retrieve violations per constraint type
    for property_shape in property_shapes:
        # Query violations grouped by constraint type for the Property Shape
        sparql.setQuery(f"""
            SELECT ?constraintComponent (COUNT(?violation) AS ?violationCount)
            FROM <{validation_report_uri}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                           <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
            }}
            GROUP BY ?constraintComponent
        """)
        sparql.setReturnFormat(JSON)

        try:
            violations_results = sparql.query().convert()
        except Exception as e:
            raise RuntimeError(f"Error querying Validation Report: {str(e)}")

        # Build the list of constraints and their violation counts
        constraints_info = [
            {
                "Constraint": result["constraintComponent"]["value"],
                "Violations": int(result["violationCount"]["value"])
            }
            for result in violations_results["results"]["bindings"]
        ]

        # Append information for the current Property Shape
        property_shapes_info.append({
            "PropertyShape": property_shape,
            "Constraints": constraints_info
        })

    return property_shapes_info


def get_total_constraints_count_per_node_shape(shapes_graph_uri: str = SHAPES_GRAPH_URI) -> list:
    """
    Calculate the total number of constraints (triples with predicates matching the SHACL features)
    for each Node Shape in the Shapes Graph.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".

    Returns:
        list: A JSON list where each element contains a Node Shape name and the total number of constraints.
    """
    

    # Build the SPARQL VALUES clause with full URIs for SHACL features
    shacl_features_values = " ".join([f"<{feature}>" for feature in SHACL_FEATURES])

    # SPARQL query to calculate total constraints (triples) per Node Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT ?nodeShape (COUNT(*) AS ?totalConstraints)
        FROM <{shapes_graph_uri}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
            ?propertyShape ?constraintTriple ?object .
            VALUES ?constraintTriple {{ {shacl_features_values} }}
        }}
        GROUP BY ?nodeShape
        ORDER BY ?nodeShape
    """)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
    except Exception as e:
        raise RuntimeError(f"Error querying Shapes Graph: {str(e)}")

    # Process the results and build the JSON list
    constraints_per_node_shape = [
        {
            "NodeShapeName": result["nodeShape"]["value"],
            "NumConstraints": int(result["totalConstraints"]["value"])
        }
        for result in results["results"]["bindings"]
    ]

    return constraints_per_node_shape


def get_constraints_count_for_property_shapes(
    nodeshape_name: str,
    shapes_graph_uri: str = SHAPES_GRAPH_URI
) -> list:
    """
    Calculate the constraints count for each Property Shape associated with the given Node Shape
    using a single SPARQL query.

    Args:
        nodeshape_name (str): The URI of the Node Shape to query.
        shapes_graph_uri (str): The URI of the Shapes Graph. Default is "http://ex.org/ShapesGraph".

    Returns:
        list: A JSON list containing Property Shape names and their corresponding constraints count.
    """
    # Build the SPARQL VALUES clause with SHACL features
    shacl_features_values = " ".join([f"<{feature}>" for feature in SHACL_FEATURES])

    # SPARQL query to calculate constraints count per Property Shape
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT ?propertyShape (COUNT(?constraintTriple) AS ?constraintCount)
        FROM <{shapes_graph_uri}>
        WHERE {{
            <{nodeshape_name}> <http://www.w3.org/ns/shacl#property> ?propertyShape .
            ?propertyShape ?constraintTriple ?object .
            VALUES ?constraintTriple {{ {shacl_features_values} }}
        }}
        GROUP BY ?propertyShape
        ORDER BY ?propertyShape
    """)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
    except Exception as e:
        raise RuntimeError(f"Error querying constraints for Node Shape {nodeshape_name}: {str(e)}")

    # Process the results and build the JSON list
    property_shapes_constraints = [
        {
            "PropertyShapeName": result["propertyShape"]["value"],
            "NumConstraints": int(result["constraintCount"]["value"])
        }
        for result in results["results"]["bindings"]
    ]

    return property_shapes_constraints


def get_maximum_number_of_violations_in_validation_report_for_node_shape() -> dict:
    """
    Calculate the number of violations for each Node Shape, and find the Node Shape
    with the maximum number of violations.

    Returns:
        dict: A dictionary containing the Node Shape URI and the corresponding
        maximum number of violations, in the format:
        {
            "nodeShape": "<Node Shape URI>",
            "violationCount": <number of violations>
        }
    """
    # Step 1: Query the Shapes Graph to get all Node Shapes and their Property Shapes
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?nodeShape ?propertyShape
        FROM <{SHAPES_GRAPH_URI}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)
    node_shapes_results = sparql.query().convert()

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
        sparql.setQuery(f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{VALIDATION_REPORT_URI}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
                VALUES ?propertyShape {{ {property_shapes_values} }}
            }}
        """)
        validation_results = sparql.query().convert()

        # Extract the number of violations
        violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])
        violation_counts[node_shape] = violation_count

    # Step 3: Find the Node Shape with the maximum number of violations
    if violation_counts:
        max_node_shape = max(violation_counts, key=violation_counts.get)
        return {"nodeShape": max_node_shape, "violationCount": violation_counts[max_node_shape]}

    # If no violations are found, return an empty result
    return {"nodeShape": "", "violationCount": 0}

def get_average_number_of_violations_in_validation_report_for_node_shape() -> float:
    """
    Query the Virtuoso SPARQL endpoint to calculate the average number of violations
    caused by the Property Shapes of all Node Shapes from the Validation Report.

    Returns:
        float: The average number of violations per Node Shape.
        - The result is rounded to 2 decimal places
    """
    # Step 1: Query the Shapes Graph to get all Node Shapes and their Property Shapes
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setQuery(f"""
        SELECT DISTINCT ?nodeShape ?propertyShape
        FROM <{SHAPES_GRAPH_URI}>
        WHERE {{
            ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                       <http://www.w3.org/ns/shacl#property> ?propertyShape .
        }}
    """)
    sparql.setReturnFormat(JSON)
    node_shapes_results = sparql.query().convert()

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
        sparql.setQuery(f"""
            SELECT (COUNT(?violation) AS ?violationCount)
            FROM <{VALIDATION_REPORT_URI}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> ?propertyShape .
                VALUES ?propertyShape {{ {property_shapes_values} }}
            }}
        """)
        validation_results = sparql.query().convert()

        # Extract the number of violations for this Node Shape
        violation_count = int(validation_results["results"]["bindings"][0]["violationCount"]["value"])
        total_violations += violation_count

    # Step 3: Calculate the average number of violations
    if total_node_shapes == 0:
        return 0.0  # Avoid division by zero

    average_violations = total_violations / total_node_shapes
    return round(average_violations, 2)


def get_distribution_of_violations_per_constraint(
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI,
    num_bins: int = 10,
) -> dict:
    """
    Generate data for the "Distribution of Violations per Constraint" plot in a single SPARQL query.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph to query.
        validation_report_uri (str): The URI of the Validation Report to query.
        shacl_features (set): The set of SHACL constraint predicates.
        num_bins (int): Number of bins for the plot. Default is 10.

    Returns:
        dict: A dictionary containing labels and datasets for the plot.
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


def calculate_shannon_entropy(violation_counts: dict) -> float:
    total = sum(violation_counts.values())
    if total == 0:
        return 0.0
    probabilities = [count / total for count in violation_counts.values()]
    return sum(-p * math.log2(p) for p in probabilities if p > 0)


def get_correlation_of_constraints_and_violations(
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI,
) -> list:
    """
    Provide data for a 'Correlation Between Constraints and Violations' plot.
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
    # Step 1: Fetch Node Shapes and their Property Shapes
    query_shapes = f"""
    SELECT DISTINCT ?nodeShape ?propertyShape
    FROM <{shapes_graph_uri}>
    WHERE {{
      ?nodeShape a <http://www.w3.org/ns/shacl#NodeShape> ;
                 <http://www.w3.org/ns/shacl#property> ?propertyShape .
    }}
    """
    response = requests.get(ENDPOINT_URL, params={"query": query_shapes, "format": "json"})
    response.raise_for_status()
    shapes_results = response.json()["results"]["bindings"]

    # Map each Node Shape to its Property Shapes
    node_shapes_map = {}
    for result in shapes_results:
        node_shape = result["nodeShape"]["value"]
        property_shape = result["propertyShape"]["value"]
        node_shapes_map.setdefault(node_shape, []).append(property_shape)

    # Prepare the result list
    result_data = []

    # Step 2: For each Node Shape, compute total constraints and violations distribution
    for node_shape, property_shapes in node_shapes_map.items():
        total_constraints = 0
        # We'll track how often each constraintComponent is violated
        violation_distribution = {}  # {constraintComponent: count}
        total_violations = 0

        # 2.1: Sum constraints & gather violation distribution across property shapes
        for property_shape in property_shapes:
            # Query for constraints in the property shape
            query_constraints = f"""
            SELECT ?predicate
            FROM <{shapes_graph_uri}>
            WHERE {{
                <{property_shape}> ?predicate ?object .
            }}
            """
            resp_constraints = requests.get(ENDPOINT_URL, params={"query": query_constraints, "format": "json"})
            resp_constraints.raise_for_status()
            constraints_results = resp_constraints.json()["results"]["bindings"]

            # Count matching predicates in SHACL_FEATURES
            constraints_count = sum(
                1 for item in constraints_results
                if item["predicate"]["value"] in SHACL_FEATURES
            )
            total_constraints += constraints_count

            # Query for the distribution of violations by sourceConstraintComponent
            query_violations = f"""
            SELECT ?constraintComponent (COUNT(*) AS ?count)
            FROM <{validation_report_uri}>
            WHERE {{
                ?violation <http://www.w3.org/ns/shacl#sourceShape> <{property_shape}> ;
                           <http://www.w3.org/ns/shacl#sourceConstraintComponent> ?constraintComponent .
            }}
            GROUP BY ?constraintComponent
            """
            resp_violations = requests.get(ENDPOINT_URL, params={"query": query_violations, "format": "json"})
            resp_violations.raise_for_status()
            violation_results = resp_violations.json()["results"]["bindings"]

            # Accumulate violation distribution
            for row in violation_results:
                component = row["constraintComponent"]["value"]
                count = int(row["count"]["value"])
                total_violations += count
                violation_distribution[component] = violation_distribution.get(component, 0) + count

        # 2.2: Compute violation entropy
        violation_entropy = calculate_shannon_entropy(violation_distribution)

        # 2.3: Build one entry for this Node Shape
        entry = {
            "violation_entropy": round(violation_entropy, 2),
            "num_violations": total_violations,
            "num_constraints": total_constraints
        }
        result_data.append(entry)

    return result_data
