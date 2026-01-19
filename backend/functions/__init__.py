"""
SHACL Dashboard - Functions Package

This package contains the core service modules for the SHACL Dashboard backend.
It provides services for loading and querying SHACL validation reports,
generating statistics and visualizations, and interacting with the Virtuoso database.

Modules:
    validation_statistics_service: Basic statistical counts and metrics
    violation_analysis_service: Violation breakdowns by entity
    distribution_analysis_service: Distribution calculations for visualizations
    validation_report_service: Detailed report generation and most violated entity analysis
    utility_functions: Utility helpers for prefix extraction, RDF parsing, benchmarking
    landing_service: Services for loading RDF data into the Virtuoso database
    shapes_overview_service: Services for shapes graph analysis and metrics
    virtuoso_service: Core database connectivity and query services
"""

from .virtuoso_service import (
    get_most_violated_constraint_for_node_shape,
    get_number_of_property_shapes_for_node_shape,
    get_all_shapes_names,
    get_all_focus_node_names,
    get_all_property_path_names,
    get_all_constraint_components_names,
    get_violations_for_shape_name,
    get_number_of_shapes_in_shapes_graph,
    map_property_shapes_to_node_shapes,
    get_shape_from_shapes_graph,
)

from .landing_service import (
    load_graphs
)

# NEW: Import from split modules
from .validation_statistics_service import (
    get_number_of_node_shapes,
    get_number_of_node_shapes_with_violations,
    get_number_of_paths_in_shapes_graph,
    get_number_of_paths_with_violations,
    get_number_of_focus_nodes_in_validation_report,
    get_number_of_violations_in_validation_report,
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

# NEW: Import from validation report service
from .validation_report_service import (
    generate_validation_details_report,
    get_most_violated_node_shape,
    get_most_violated_path,
    get_most_violated_focus_node,
    get_most_frequent_constraint_component,
    get_distinct_constraint_components_count,
    get_distinct_constraints_count_in_shapes,
)

# NEW: Import from utility functions
from .utility_functions import (
    get_prefixes_from_endpoint,
    parse_rdf_list,
    benchmark_function_execution,
    debug_check_data,
)

from .shapes_overview_service import (
    get_number_of_violations_for_node_shape,
    get_number_of_violated_focus_for_node_shape,
    get_number_of_property_paths_for_node_shape,
    get_number_of_constraints_for_node_shape,
    get_property_shapes,
    get_number_of_violations_per_constraint_type_for_property_shape,
    get_total_constraints_count_per_node_shape,
    get_constraints_count_for_property_shapes,
    get_maximum_number_of_violations_in_validation_report_for_node_shape,
    get_average_number_of_violations_in_validation_report_for_node_shape,
    get_distribution_of_violations_per_constraint,
    get_correlation_of_constraints_and_violations,
    get_node_shape_details_table,
    get_property_shape_with_violations,
    get_node_shape_with_violations,
)

__all__ = [
    # Landing service
    "load_graphs",
    
    # Virtuoso service
    "get_most_violated_constraint_for_node_shape",
    "get_number_of_property_shapes_for_node_shape",
    "get_all_shapes_names",
    "get_all_focus_node_names",
    "get_all_property_path_names",
    "get_all_constraint_components_names",
    "get_violations_for_shape_name",
    "get_number_of_shapes_in_shapes_graph",
    "map_property_shapes_to_node_shapes",
    "get_shape_from_shapes_graph",
    
    # Validation statistics service
    "get_number_of_node_shapes",
    "get_number_of_node_shapes_with_violations",
    "get_number_of_paths_in_shapes_graph",
    "get_number_of_paths_with_violations",
    "get_number_of_focus_nodes_in_validation_report",
    "get_number_of_violations_in_validation_report",
    "count_triples",
    
    # Violation analysis service  
    "get_violations_per_node_shape",
    "get_violations_per_path",
    "get_violations_per_focus_node",
    
    # Distribution analysis service
    "distribution_of_violations_per_shape",
    "distribution_of_violations_per_path",
    "distribution_of_violations_per_focus_node",
    "get_distribution_of_violations_per_constraint_component",
    "distribution_of_violations_per_path_with_adaptive_bins",
    
    # Validation report service
    "generate_validation_details_report",
    "get_most_violated_node_shape",
    "get_most_violated_path",
    "get_most_violated_focus_node",
    "get_most_frequent_constraint_component",
    "get_distinct_constraint_components_count",
    "get_distinct_constraints_count_in_shapes",
    
    # Utility functions
    "get_prefixes_from_endpoint",
    "parse_rdf_list",
    "benchmark_function_execution",
    "debug_check_data",
    
    # Shapes overview service
    "get_number_of_violations_for_node_shape",
    "get_number_of_violated_focus_for_node_shape",
    "get_number_of_property_paths_for_node_shape",
    "get_number_of_constraints_for_node_shape",
    "get_property_shapes",
    "get_number_of_violations_per_constraint_type_for_property_shape",
    "get_total_constraints_count_per_node_shape",
    "get_constraints_count_for_property_shapes",
    "get_maximum_number_of_violations_in_validation_report_for_node_shape",
    "get_average_number_of_violations_in_validation_report_for_node_shape",
    "get_distribution_of_violations_per_constraint",
    "get_correlation_of_constraints_and_violations",
    "get_node_shape_details_table",
    "get_property_shape_with_violations",
    "get_node_shape_with_violations",
]

