import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENDPOINT_URL, SHAPES_GRAPH_URI, VALIDATION_REPORT_URI, SHACL_FEATURES
from virtuoso_service import *

"""
Service Test Module

This module contains test functions for validating the functionality of the 
SHACL Dashboard services.

It provides test functions to verify:
1. Database connectivity
2. Query execution
3. Data loading operations
4. Result format validation
5. Performance benchmarking

This module is designed for internal testing and debugging purposes.
It can be run directly to execute tests against the configured 
Virtuoso database endpoint.

Example usage:
    result = get_shape_from_shapes_graph(["http://shaclshapes.org/AmphibianShape"])
    print(len(result["http://shaclshapes.org/AmphibianShape"]["propertyShapes"]))
"""

#load_graphs("/Users/kejin/Developer/Trav-Exp/source/Datasets/", "shape30_clean.ttl", "EnDe50_result_.ttl")
#result = get_violations_for_shape_name("http://shaclshapes.org/seeAlsoSnookerPlayerShapeProperty","http://ex.org/ValidationReports")

#result = map_property_shapes_to_node_shapes("http://ex.org/ValidationReports", "http://ex.org/ShapesGraph")

result = get_shape_from_shapes_graph(["http://shaclshapes.org/AmphibianShape"])
print(len(result["http://shaclshapes.org/AmphibianShape"]["propertyShapes"]))
