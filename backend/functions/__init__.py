"""
SHACL Dashboard - Functions Package

This package contains the core service modules for the SHACL Dashboard backend.
It provides services for loading and querying SHACL validation reports,
generating statistics and visualizations, and interacting with the Virtuoso database.

Modules:
    homepage_service: Services for the main dashboard page and statistics
    landing_service: Services for loading RDF data into the Virtuoso database
    shape_view_service: Services for detailed shape inspection views
    shapes_overview_service: Services for shapes graph analysis and metrics
    virtuoso_service: Core database connectivity and query services
"""

from .virtuoso_service import (
    #get_number_of_constraints_for_node_shape,
    get_most_violated_constraint_for_node_shape,
    get_number_of_property_shapes_for_node_shape,
    get_all_shapes_names,
    get_all_focus_node_names,
    get_all_property_path_names,
    get_all_constraint_components_names,
    get_violations_for_shape_name,
    get_number_of_shapes_in_shapes_graph,
    # get_number_of_violations_in_validation_report,
    map_property_shapes_to_node_shapes,
    get_shape_from_shapes_graph,
    get_maximum_number_of_violations_in_validation_report_for_node_shape,
    get_average_number_of_violations_in_validation_report_for_node_shape,
    
)

from .landing_service import (
    load_graphs
)

from .homepage_service import (
    get_number_of_node_shapes,
    get_number_of_node_shapes_with_violations,
    get_number_of_paths_in_shapes_graph,
    get_number_of_paths_with_violations,
    get_number_of_focus_nodes_in_validation_report,
    get_violations_per_node_shape,
    get_violations_per_path,
    get_violations_per_focus_node,
    get_number_of_violations_in_validation_report,
    distribution_of_violations_per_shape,
    distribution_of_violations_per_path,
    distribution_of_violations_per_focus_node,
    generate_validation_details_report,
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
)

__all__ = [
    "load_graphs",
    "get_number_of_constraints_for_node_shape",
    "get_number_of_violations_for_node_shape",
    "get_most_violated_constraint_for_node_shape",
    "get_number_of_property_paths_for_node_shape",
    "get_number_of_property_shapes_for_node_shape",
    "get_all_shapes_names",
    "get_all_focus_node_names",
    "get_all_property_path_names",
    "get_all_constraint_components_names",
    "get_violations_for_shape_name",
    "get_number_of_shapes_in_shapes_graph",
    "get_number_of_violations_in_validation_report",
    "map_property_shapes_to_node_shapes",
    "get_shape_from_shapes_graph",
    "get_maximum_number_of_violations_in_validation_report_for_node_shape",
    "get_average_number_of_violations_in_validation_report_for_node_shape",
    "get_number_of_node_shapes",
    "get_number_of_node_shapes_with_violations",
    "get_number_of_paths_in_shapes_graph",
    "get_number_of_paths_with_violations",
    "get_number_of_focus_nodes_in_validation_report",
    "get_violations_per_node_shape",
    "get_violations_per_path",
    "get_violations_per_focus_node",
    "get_number_of_violated_focus_for_node_shape",
    "get_property_shapes",
    "get_number_of_violations_per_constraint_type_for_property_shape",
    "get_total_constraints_count_per_node_shape",
    "get_constraints_count_for_property_shapes",
    "distribution_of_violations_per_shape",
    "distribution_of_violations_per_path",
    "distribution_of_violations_per_focus_node",
    "generate_validation_details_report",
    
]
