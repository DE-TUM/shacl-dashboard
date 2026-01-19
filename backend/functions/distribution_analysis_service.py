"""
Distribution Analysis Service Module

This module provides functions for calculating statistical distributions of violations
across different groupings. These functions generate data formatted for visualization
in bar charts and histograms.

Functions:
- distribution_of_violations_per_shape: Violation distribution across node shapes
- distribution_of_violations_per_path: Violation distribution across paths
- distribution_of_violations_per_focus_node: Violation distribution across focus nodes
- get_distribution_of_violations_per_constraint_component: Distribution by constraint type
- distribution_of_violations_per_path_with_adaptive_bins: Path distribution with adaptive binning
"""

import sys
import os
from typing import List, Dict, Any
import logging
import math
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI

logger = logging.getLogger(__name__)


def distribution_of_violations_per_shape(
    shapes_graph_uri: str = SHAPES_GRAPH_URI,
    validation_report_uri: str = VALIDATION_REPORT_URI
) -> Dict[str, Any]:
    """
    Prepare data for a bar chart showing the frequency of Node Shapes in different violation ranges.

    Args:
        shapes_graph_uri (str): The URI of the Shapes Graph to query. Default is "http://ex.org/ShapesGraph".
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        Dict[str, Any]: A dictionary formatted for bar chart visualization with 'labels' and 'datasets' keys.
    """
    from .violation_analysis_service import get_violations_per_node_shape
    
    # Step 1: Get the violation data for each Node Shape
    violations_data = get_violations_per_node_shape(shapes_graph_uri, validation_report_uri)

    # Step 2: Extract the maximum number of violations
    max_violations = max([item["NumViolations"] for item in violations_data]) if violations_data else 0

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


def distribution_of_violations_per_path(validation_report_uri: str = VALIDATION_REPORT_URI) -> Dict[str, Any]:
    """
    Prepare data for a bar chart showing the distribution of violations per unique sh:resultPath
    in the Validation Report, grouped by violation count ranges.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        Dict[str, Any]: A dictionary formatted for bar chart visualization with 'labels' and 'datasets' keys.
    """
    from .violation_analysis_service import get_violations_per_path
    
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


def distribution_of_violations_per_focus_node(validation_report_uri: str = VALIDATION_REPORT_URI) -> Dict[str, Any]:
    """
    Prepare data for a bar chart showing the distribution of violations per unique sh:focusNode
    in the Validation Report, grouped by violation count ranges.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        Dict[str, Any]: A dictionary formatted for bar chart visualization with 'labels' and 'datasets' keys.
    """
    from .violation_analysis_service import get_violations_per_focus_node
    
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


def get_distribution_of_violations_per_constraint_component(
    validation_report_uri: str = VALIDATION_REPORT_URI,
) -> dict:
    """
    Generate data for a bar chart representing the distribution of violations per constraint component.

    Args:
        validation_report_uri: The URI of the Validation Report. Default is VALIDATION_REPORT_URI.

    Returns:
        Dict[str, Any]: A dictionary formatted for a bar chart visualization:
            - 'labels' (List[str]): Range labels (e.g., ['0-10', '11-20', ...])
            - 'datasets' (List[Dict]): Chart datasets with label and data arrays
            
    Example:
        {
            'labels': ['0-10', '11-20', ...],
            'datasets': [
                {
                    'label': 'Number of Constraint Components',
                    'data': [5, 12, ...],
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


def distribution_of_violations_per_path_with_adaptive_bins(validation_report_uri: str = VALIDATION_REPORT_URI) -> dict:
    """
    Prepare data for a bar chart showing the distribution of violations per unique sh:resultPath
    in the Validation Report, grouped by adaptive violation count ranges.

    Args:
        validation_report_uri (str): The URI of the Validation Report to query. Default is "http://ex.org/ValidationReport".

    Returns:
        dict: A dictionary formatted for bar chart visualization with labels and datasets.
    """
    from .violation_analysis_service import get_violations_per_path
    
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
