import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI, SHACL_FEATURES, ISQL_PORT, ISQL_USERNAME, ISQL_PASSWORD
from SPARQLWrapper import SPARQLWrapper, JSON
from .prefix_utils import cache_prefixes, extract_prefixes_from_sparql_graphs
import logging

logger = logging.getLogger(__name__)

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
    # Validate input types
    if not all(isinstance(arg, str) for arg in [directory, shapes_file, report_file]):
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

    logger.info("Executing ISQL command to load graphs...")

    try:
        # Execute ISQL command
        process = subprocess.run(
            ["isql", ISQL_PORT, ISQL_USERNAME, ISQL_PASSWORD],
            input=isql_command,
            text=True,
            capture_output=True,
            check=True
        )

        # Output success message
        logger.info("ISQL command executed successfully")
        logger.debug("ISQL output: %s", process.stdout)
        
        # Extract prefixes from the actual SPARQL graphs
        logger.info("Extracting prefixes from SPARQL graphs...")
        try:
            prefixes = extract_prefixes_from_sparql_graphs(
                ENDPOINT_URL,
                [SHAPES_GRAPH_URI, VALIDATION_REPORT_URI]
            )
            cache_prefixes(prefixes)
            logger.info("Total prefixes cached: %d", len(prefixes))
        except Exception as e:
            logger.error("Error extracting prefixes from SPARQL graphs: %s", e)
            logger.warning("Using minimal fallback prefixes")
            cache_prefixes({'sh': 'http://www.w3.org/ns/shacl#'})

    except subprocess.CalledProcessError as e:
        # Handle command execution failure
        logger.error("ISQL command execution failed: %s", e.stderr)
        raise RuntimeError(f"ISQL command execution failed: {e.stderr}")

    except FileNotFoundError:
        # Handle missing ISQL tool
        logger.error("ISQL tool not found. Please check if Virtuoso is installed correctly.")
        raise RuntimeError("ISQL tool not found")
