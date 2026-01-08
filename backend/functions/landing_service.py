import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI, SHACL_FEATURES
from SPARQLWrapper import SPARQLWrapper, JSON

"""
Landing Service Module

This module provides functionality for loading RDF data into a Virtuoso database
for SHACL validation visualization. It manages the initial data loading operations
for the SHACL Dashboard.

The primary function `load_graphs` uses the Virtuoso ISQL command-line interface
to load SHACL shapes and validation report files into named graphs in the database.
It handles parameter validation, subprocess execution, and error handling.

Key functions:
- load_graphs: Load RDF files containing SHACL shapes and validation reports

Configuration:
- ENDPOINT_URL: SPARQL endpoint URL (default: http://localhost:8890/sparql)
- SHAPES_GRAPH_URI: URI for the shapes graph (default: http://ex.org/ShapesGraph)
- VALIDATION_REPORT_URI: URI for validation report (default: http://ex.org/ValidationReport)
"""

# Global variables for SPARQL
#ENDPOINT_URL = "http://localhost:8890/sparql"
#SHAPES_GRAPH_URI = "http://ex.org/ShapesGraph"
#VALIDATION_REPORT_URI = "http://ex.org/ValidationReport"

def load_graphs(directory: str, shapes_file: str, report_file: str, isql_port: str = "1111", username: str = "dba", password: str = "dba"):
    """
    Load two RDF files (ShapesGraph and ValidationReport) into Virtuoso using ISQL.

    Args:
        directory (str): Directory containing the RDF files.
        shapes_file (str): Name of the ShapesGraph file.
        report_file (str): Name of the ValidationReport file.
        isql_port (str, optional): ISQL port. Default is "1111".
        username (str, optional): ISQL username. Default is "dba".
        password (str, optional): ISQL password. Default is "dba".

    Raises:
        TypeError: If any of the arguments are not strings.
        ValueError: If any of the arguments are empty strings.
    """
    # Validate input types
    if not all(isinstance(arg, str) for arg in [directory, shapes_file, report_file, isql_port, username, password]):
        raise TypeError("All arguments must be strings.")

    # Validate input values
    if not all(arg.strip() for arg in [directory, shapes_file, report_file]):
        raise ValueError("Directory, shapes_file, and report_file cannot be empty strings.")

    # Construct ISQL command for loading RDF files
    isql_command = f"""
    ld_dir('{directory}', '{shapes_file}', '{SHAPES_GRAPH_URI}');
    ld_dir('{directory}', '{report_file}', '{VALIDATION_REPORT_URI}');
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

        # Output success message
        print("ISQL command executed successfully!")
        print(process.stdout)

    except subprocess.CalledProcessError as e:
        # Handle command execution failure
        print("ISQL command execution failed!")
        print(e.stderr)

    except FileNotFoundError:
        # Handle missing ISQL tool
        print("ISQL tool not found. Please check if Virtuoso is installed correctly.")
