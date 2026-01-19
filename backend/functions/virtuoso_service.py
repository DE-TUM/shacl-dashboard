"""
Virtuoso Service Module (Re-export)

This module re-exports functions from specialized modules to maintain
backward compatibility with existing code that imports from this module.

All functions have been split into smaller, more maintainable modules:
- virtuoso_database: Database operations (loading, clearing graphs)
- entity_retrieval: Retrieving entities from graphs
- shape_retrieval: Shape-specific retrieval and mapping functions
"""

import logging

logger = logging.getLogger(__name__)
logger.warning(
    "virtuoso_service module is deprecated. "
    "Please import from specialized modules: virtuoso_database, "
    "entity_retrieval, shape_retrieval."
)

# Import from virtuoso_database
from .virtuoso_database import (
    clear_graphs_only,
    load_graphs
)

# Import from entity_retrieval
from .entity_retrieval import (
    get_all_shapes_names,
    get_all_focus_node_names,
    get_all_property_path_names,
    get_all_constraint_components_names,
    get_violations_for_shape_name,
    get_number_of_shapes_in_shapes_graph,
    get_number_of_violations_in_validation_report
)

# Import from shape_retrieval
from .shape_retrieval import (
    map_property_shapes_to_node_shapes,
    get_shape_from_shapes_graph,
    get_number_of_property_shapes_for_node_shape,
    get_most_violated_constraint_for_node_shape
)

# Define __all__ to explicitly export all functions
__all__ = [
    # From virtuoso_database
    'clear_graphs_only',
    'load_graphs',
    
    # From entity_retrieval
    'get_all_shapes_names',
    'get_all_focus_node_names',
    'get_all_property_path_names',
    'get_all_constraint_components_names',
    'get_violations_for_shape_name',
    'get_number_of_shapes_in_shapes_graph',
    'get_number_of_violations_in_validation_report',
    
    # From shape_retrieval
    'map_property_shapes_to_node_shapes',
    'get_shape_from_shapes_graph',
    'get_number_of_property_shapes_for_node_shape',
    'get_most_violated_constraint_for_node_shape',
]
