import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SHAPES_GRAPH_URI, VALIDATION_REPORT_URI, DATA_DIR_IN_DOCKER, DOCKER_CONTAINER_NAME, ISQL_PORT, ISQL_USERNAME, ISQL_PASSWORD
import logging

logger = logging.getLogger(__name__)

"""
Virtuoso Database Module

This module provides core functionality for interacting with the Virtuoso
database, including clearing graphs and loading RDF data.

Key functions:
- clear_graphs_only: Clear specific graphs from Virtuoso
- load_graphs: Load RDF files into named graphs
"""


def clear_graphs_only() -> None:
    """
    Clear specific graphs from Virtuoso using ISQL via Docker.

    Raises:
        CalledProcessError: If clearing a graph fails.
        FileNotFoundError: If ISQL or Docker is not found.
    """
    test_command = "SELECT 1;\n"

    logger.info("Running ISQL test command...")

    try:
        result = subprocess.run(
            ["docker", "exec", "-i", DOCKER_CONTAINER_NAME, "isql", ISQL_PORT, ISQL_USERNAME, ISQL_PASSWORD],
            input=test_command,
            text=True,
            capture_output=True,
            check=True
        )
        logger.info("ISQL test command executed successfully: %s", result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error("ISQL test command failed: %s", e.stderr)


def load_graphs(directory: str, shapes_file: str, report_file: str) -> None:
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

    # Clean graphs before loading
    for graph_uri in [SHAPES_GRAPH_URI, VALIDATION_REPORT_URI]:
        isql_command_clear = f"SPARQL DROP GRAPH <{graph_uri}>;"
        try:
            subprocess.run(
                ["docker", "exec", "-i", DOCKER_CONTAINER_NAME, "isql", ISQL_PORT, ISQL_USERNAME, ISQL_PASSWORD],
                input=isql_command_clear,
                text=True,
                check=True
            )
            logger.info("Cleared graph <%s>", graph_uri)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to clear graph <%s>: %s", graph_uri, e.stderr)

    # Clean load list
    for ttl_file in [shapes_file, report_file]:
        ttl_filename = os.path.basename(ttl_file)
        # Use parameterized query to prevent SQL injection
        isql_command_cleanup = f"""
        DELETE FROM DB.DBA.load_list WHERE ll_file = '{DATA_DIR_IN_DOCKER}/{ttl_filename}';
        """
        try:
            subprocess.run(
                ["docker", "exec", "-i", DOCKER_CONTAINER_NAME, "isql", ISQL_PORT, ISQL_USERNAME, ISQL_PASSWORD],
                input=isql_command_cleanup,
                text=True,
                check=True
            )
            logger.info("Cleaned up load_list for %s", ttl_filename)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to clean load_list for %s: %s", ttl_filename, e.stderr)

    # ISQL commands for both files
    isql_command = f"""
    ld_dir('{DATA_DIR_IN_DOCKER}', '{shapes_file}', '{SHAPES_GRAPH_URI}');
    ld_dir('{DATA_DIR_IN_DOCKER}', '{report_file}', '{VALIDATION_REPORT_URI}');
    rdf_loader_run();
    """

    logger.info("Executing ISQL command to load graphs...")

    try:
        # Execute ISQL command
        process = subprocess.run(
            ["docker", "exec", "-i", DOCKER_CONTAINER_NAME, "isql", ISQL_PORT, ISQL_USERNAME, ISQL_PASSWORD],
            input=isql_command,
            text=True,
            capture_output=True,
            check=True
        )
        logger.info("ISQL command executed successfully")
        logger.debug("ISQL output: %s", process.stdout)

    except subprocess.CalledProcessError as e:
        logger.error("ISQL command execution failed: %s", e.stderr)
        raise RuntimeError(f"Failed to load graphs: {e.stderr}")

    except FileNotFoundError:
        logger.error("ISQL tool not found. Please check if Virtuoso is installed correctly.")
        raise RuntimeError("ISQL tool not found")
