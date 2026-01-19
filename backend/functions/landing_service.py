import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging

# Import load_graphs from virtuoso_service to avoid duplication
from .virtuoso_service import load_graphs

logger = logging.getLogger(__name__)

"""
Landing Service Module

This module provides functionality for loading RDF data into a Virtuoso database
for SHACL validation visualization. It manages the initial data loading operations
for the SHACL Dashboard.

The primary function `load_graphs` is imported from virtuoso_service to avoid
code duplication and maintain a single source of truth for graph loading operations.

Key functions:
- load_graphs: Load RDF files containing SHACL shapes and validation reports
  (imported from virtuoso_service)

Configuration:
- ENDPOINT_URL: SPARQL endpoint URL (default: http://localhost:8890/sparql)
- SHAPES_GRAPH_URI: URI for the shapes graph (default: http://ex.org/ShapesGraph)
- VALIDATION_REPORT_URI: URI for validation report (default: http://ex.org/ValidationReport)
"""

# Note: load_graphs function is now imported from virtuoso_service.py
# This eliminates code duplication and ensures consistent behavior
