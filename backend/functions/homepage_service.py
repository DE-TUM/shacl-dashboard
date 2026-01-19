"""
Homepage Service Module (DEPRECATED)

This module has been split into specialized service modules for better organization and maintainability.

Functions have been moved to:
- validation_statistics_service: get_number_of_violations_in_validation_report, get_number_of_node_shapes, etc.
- violation_analysis_service: get_violations_per_node_shape, get_violations_per_path, etc.
- distribution_analysis_service: distribution_of_violations_per_shape, get_distribution_of_violations_per_constraint_component, etc.
- validation_report_service: generate_validation_details_report, get_most_violated_node_shape, etc.
- utility_functions: get_prefixes_from_endpoint, parse_rdf_list, benchmark_function_execution, etc.

For backward compatibility, all functions are re-exported from __init__.py.
Please update your imports to use the new specialized modules.

This file will be removed in a future version.
"""

import logging

logger = logging.getLogger(__name__)
logger.warning(
    "homepage_service module is deprecated. "
    "Please import from specialized modules: validation_statistics_service, "
    "violation_analysis_service, distribution_analysis_service, etc."
)

# Backward compatibility: Re-export all functions from new modules
from .validation_statistics_service import (
    get_number_of_violations_in_validation_report,
    get_number_of_node_shapes,
    get_number_of_node_shapes_with_violations,
    get_number_of_paths_in_shapes_graph,
    get_number_of_paths_with_violations,
    get_number_of_focus_nodes_in_validation_report,
    count_triples,
)

from .violation_analysis_service import (
    get_violations_per_node_shape,
    get_violations_per_path,
    get_violations_per_focus_node,
)

from .distribution_analysis_service import (
    distribution_of_violations_per_shape,
    distribution_of_violations_per_path,
    distribution_of_violations_per_focus_node,
    get_distribution_of_violations_per_constraint_component,
    distribution_of_violations_per_path_with_adaptive_bins,
)

from .validation_report_service import (
    generate_validation_details_report,
    get_most_violated_node_shape,
    get_most_violated_path,
    get_most_violated_focus_node,
    get_most_frequent_constraint_component,
    get_distinct_constraint_components_count,
    get_distinct_constraints_count_in_shapes,
)

from .utility_functions import (
    get_prefixes_from_endpoint,
    parse_rdf_list,
    benchmark_function_execution,
    debug_check_data,
)

__all__ = [
    # Validation statistics
    "get_number_of_violations_in_validation_report",
    "get_number_of_node_shapes",
    "get_number_of_node_shapes_with_violations",
    "get_number_of_paths_in_shapes_graph",
    "get_number_of_paths_with_violations",
    "get_number_of_focus_nodes_in_validation_report",
    "count_triples",
    
    # Violation analysis
    "get_violations_per_node_shape",
    "get_violations_per_path",
    "get_violations_per_focus_node",
    
    # Distribution analysis
    "distribution_of_violations_per_shape",
    "distribution_of_violations_per_path",
    "distribution_of_violations_per_focus_node",
    "get_distribution_of_violations_per_constraint_component",
    "distribution_of_violations_per_path_with_adaptive_bins",
    
    # Validation report
    "generate_validation_details_report",
    "get_most_violated_node_shape",
    "get_most_violated_path",
    "get_most_violated_focus_node",
    "get_most_frequent_constraint_component",
    "get_distinct_constraint_components_count",
    "get_distinct_constraints_count_in_shapes",
    
    # Utilities
    "get_prefixes_from_endpoint",
    "parse_rdf_list",
    "benchmark_function_execution",
    "debug_check_data",
]
