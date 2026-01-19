"""
Shapes Overview Service Module (Re-export)

This module re-exports functions from specialized modules to maintain
backward compatibility with existing code that imports from this module.

All functions have been split into smaller, more maintainable modules:
- node_shape_metrics: Node shape-specific metrics and mappings
- property_shape_operations: Property shape operations and violations
- shape_statistics: Statistical calculations for shapes
- shape_analytics: Advanced analytics and correlation analysis
"""

import logging

logger = logging.getLogger(__name__)
logger.warning(
    "shapes_overview_service module is deprecated. "
    "Please import from specialized modules: node_shape_metrics, "
    "property_shape_operations, shape_statistics, shape_analytics."
)

# Import from node_shape_metrics
from .node_shape_metrics import (
    get_property_to_node_map,
    get_number_of_violations_for_node_shape,
    get_number_of_violated_focus_for_node_shape,
    get_number_of_property_paths_for_node_shape,
    get_number_of_constraints_for_node_shape
)

# Import from property_shape_operations
from .property_shape_operations import (
    get_property_shapes,
    get_number_of_violations_per_constraint_type_for_property_shape,
    get_property_shape_with_violations,
    get_node_shape_with_violations,
    get_total_constraints_count_per_node_shape,
    get_constraints_count_for_property_shapes
)

# Import from shape_statistics
from .shape_statistics import (
    get_maximum_number_of_violations_in_validation_report_for_node_shape,
    get_average_number_of_violations_in_validation_report_for_node_shape,
    get_node_shape_with_most_unique_constraints
)

# Import from shape_analytics
from .shape_analytics import (
    get_distribution_of_violations_per_constraint,
    calculate_shannon_entropy,
    get_correlation_of_constraints_and_violations,
    get_node_shape_details_table
)

# Define __all__ to explicitly export all functions
__all__ = [
    # From node_shape_metrics
    'get_property_to_node_map',
    'get_number_of_violations_for_node_shape',
    'get_number_of_violated_focus_for_node_shape',
    'get_number_of_property_paths_for_node_shape',
    'get_number_of_constraints_for_node_shape',
    
    # From property_shape_operations
    'get_property_shapes',
    'get_number_of_violations_per_constraint_type_for_property_shape',
    'get_property_shape_with_violations',
    'get_node_shape_with_violations',
    'get_total_constraints_count_per_node_shape',
    'get_constraints_count_for_property_shapes',
    
    # From shape_statistics
    'get_maximum_number_of_violations_in_validation_report_for_node_shape',
    'get_average_number_of_violations_in_validation_report_for_node_shape',
    'get_node_shape_with_most_unique_constraints',
    
    # From shape_analytics
    'get_distribution_of_violations_per_constraint',
    'calculate_shannon_entropy',
    'get_correlation_of_constraints_and_violations',
    'get_node_shape_details_table',
]
