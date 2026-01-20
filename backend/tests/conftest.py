"""
Pytest Configuration and Fixtures

This module provides shared fixtures and configuration for all test files.
It includes mock SPARQL executors, sample data, and common test utilities.
"""

import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


@pytest.fixture
def mock_sparql_executor():
    """
    Mock SparqlQueryExecutor for testing without actual database calls.
    
    Returns:
        Mock: Configured mock executor with common methods
    """
    executor = Mock()
    executor.execute_query = Mock()
    executor.execute_count_query = Mock(return_value=0)
    executor.execute_ask_query = Mock(return_value=False)
    return executor


@pytest.fixture
def sample_sparql_results():
    """
    Sample SPARQL query results in the expected JSON format.
    
    Returns:
        dict: Sample SPARQL results
    """
    return {
        "results": {
            "bindings": [
                {
                    "shape": {"type": "uri", "value": "http://ex.org/PersonShape"},
                    "count": {"type": "literal", "value": "10"}
                },
                {
                    "shape": {"type": "uri", "value": "http://ex.org/CompanyShape"},
                    "count": {"type": "literal", "value": "5"}
                }
            ]
        }
    }


@pytest.fixture
def sample_graph_uris():
    """
    Sample graph URIs for testing.
    
    Returns:
        dict: Dictionary of common graph URIs
    """
    return {
        "shapes_graph": "http://ex.org/ShapesGraph",
        "validation_report": "http://ex.org/ValidationReport"
    }


@pytest.fixture
def sample_node_shapes():
    """
    Sample node shape data for testing.
    
    Returns:
        list: List of sample node shapes
    """
    return [
        "http://ex.org/PersonShape",
        "http://ex.org/CompanyShape",
        "http://ex.org/AddressShape"
    ]


@pytest.fixture
def sample_violations():
    """
    Sample violation data for testing.
    
    Returns:
        dict: Sample SPARQL results with violation data
    """
    return {
        "results": {
            "bindings": [
                {
                    "violation": {"type": "uri", "value": "http://ex.org/Violation1"},
                    "focusNode": {"type": "uri", "value": "http://ex.org/Person1"},
                    "resultPath": {"type": "uri", "value": "http://ex.org/name"},
                    "value": {"type": "literal", "value": ""},
                    "message": {"type": "literal", "value": "Value required"},
                    "sourceShape": {"type": "uri", "value": "http://ex.org/PersonNameShape"},
                    "severity": {"type": "uri", "value": "http://www.w3.org/ns/shacl#Violation"},
                    "constraintComponent": {"type": "uri", "value": "http://www.w3.org/ns/shacl#MinLengthConstraintComponent"}
                }
            ]
        }
    }


@pytest.fixture
def mock_sparql_wrapper():
    """
    Mock SPARQLWrapper for testing HTTP interactions.
    
    Returns:
        Mock: Configured SPARQLWrapper mock
    """
    wrapper = Mock()
    wrapper.setQuery = Mock()
    wrapper.setReturnFormat = Mock()
    wrapper.query = Mock()
    wrapper.query.return_value.convert = Mock(return_value={"results": {"bindings": []}})
    return wrapper


# Configure pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
