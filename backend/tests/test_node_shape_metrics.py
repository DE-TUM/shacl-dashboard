"""
Unit Tests for node_shape_metrics.py

Tests for functions that calculate metrics and statistics specific to node shapes.
"""

import pytest
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from functions.node_shape_metrics import (
    get_property_to_node_map,
    get_number_of_violations_for_node_shape,
    get_number_of_violated_focus_for_node_shape,
    get_number_of_property_paths_for_node_shape,
    get_number_of_constraints_for_node_shape
)
from validators import ValidationError


class TestGetPropertyToNodeMap:
    """Tests for get_property_to_node_map function."""
    
    def test_returns_mapping_dict(self, mock_sparql_executor):
        """Test that function returns a dictionary mapping properties to nodes."""
        mock_sparql_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "propertyShape": {"value": "http://ex.org/Prop1"},
                        "nodeShape": {"value": "http://ex.org/Node1"}
                    },
                    {
                        "propertyShape": {"value": "http://ex.org/Prop2"},
                        "nodeShape": {"value": "http://ex.org/Node1"}
                    }
                ]
            }
        }
        
        result = get_property_to_node_map(
            "http://ex.org/ShapesGraph",
            executor=mock_sparql_executor
        )
        
        assert isinstance(result, dict)
        assert result["http://ex.org/Prop1"] == "http://ex.org/Node1"
        assert result["http://ex.org/Prop2"] == "http://ex.org/Node1"
    
    def test_empty_graph_returns_empty_dict(self, mock_sparql_executor):
        """Test that empty graph returns empty dictionary."""
        mock_sparql_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = get_property_to_node_map(
            "http://ex.org/EmptyGraph",
            executor=mock_sparql_executor
        )
        
        assert result == {}
    
    def test_invalid_uri_rejected(self, mock_sparql_executor):
        """Test that invalid graph URI is rejected."""
        with pytest.raises(ValidationError):
            get_property_to_node_map(
                "not-a-uri",
                executor=mock_sparql_executor
            )


class TestGetNumberOfViolationsForNodeShape:
    """Tests for get_number_of_violations_for_node_shape function."""
    
    def test_returns_violation_count(self, mock_sparql_executor):
        """Test that function returns violation count for a node shape."""
        # Mock property shapes query
        mock_sparql_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"propertyShape": {"value": "http://ex.org/Prop1"}},
                    {"propertyShape": {"value": "http://ex.org/Prop2"}}
                ]
            }
        }
        
        # Mock violation count query (called after property shapes query)
        def side_effect(*args, **kwargs):
            query = args[0]
            if "COUNT(?violation)" in query:
                return {
                    "results": {
                        "bindings": [
                            {"violationCount": {"value": "10"}}
                        ]
                    }
                }
            return mock_sparql_executor.execute_query.return_value
        
        mock_sparql_executor.execute_query.side_effect = side_effect
        
        result = get_number_of_violations_for_node_shape(
            "http://ex.org/PersonShape",
            executor=mock_sparql_executor
        )
        
        # Should call execute_query twice: once for properties, once for violations
        assert mock_sparql_executor.execute_query.call_count >= 2
    
    def test_node_shape_with_no_properties_returns_zero(self, mock_sparql_executor):
        """Test that node shape with no properties returns 0 violations."""
        mock_sparql_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = get_number_of_violations_for_node_shape(
            "http://ex.org/EmptyShape",
            executor=mock_sparql_executor
        )
        
        assert result == 0
    
    def test_invalid_node_shape_uri_rejected(self, mock_sparql_executor):
        """Test that invalid node shape URI is rejected."""
        with pytest.raises(ValidationError):
            get_number_of_violations_for_node_shape(
                "invalid-uri",
                executor=mock_sparql_executor
            )
    
    def test_all_uris_validated(self, mock_sparql_executor):
        """Test that all URI parameters are validated."""
        # Invalid shapes graph URI
        with pytest.raises(ValidationError):
            get_number_of_violations_for_node_shape(
                "http://ex.org/PersonShape",
                shapes_graph_uri="invalid",
                executor=mock_sparql_executor
            )
        
        # Invalid validation report URI
        with pytest.raises(ValidationError):
            get_number_of_violations_for_node_shape(
                "http://ex.org/PersonShape",
                validation_report_uri="invalid",
                executor=mock_sparql_executor
            )


class TestGetNumberOfViolatedFocusForNodeShape:
    """Tests for get_number_of_violated_focus_for_node_shape function."""
    
    def test_returns_focus_node_count(self, mock_sparql_executor):
        """Test that function returns count of violated focus nodes."""
        # Mock two queries: first for property shapes, second for focus node count
        mock_sparql_executor.execute_query.side_effect = [
            # First call: property shapes query
            {
                "results": {
                    "bindings": [
                        {"propertyShape": {"value": "http://ex.org/Prop1"}}
                    ]
                }
            },
            # Second call: focus node count query
            {
                "results": {
                    "bindings": [
                        {"focusNodeCount": {"value": "5"}}
                    ]
                }
            }
        ]
        
        result = get_number_of_violated_focus_for_node_shape(
            "http://ex.org/PersonShape",
            executor=mock_sparql_executor
        )
        
        assert result == 5
    
    def test_node_shape_without_violations(self, mock_sparql_executor):
        """Test node shape without any violations."""
        mock_sparql_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = get_number_of_violated_focus_for_node_shape(
            "http://ex.org/ValidShape",
            executor=mock_sparql_executor
        )
        
        assert result == 0


class TestGetNumberOfPropertyPathsForNodeShape:
    """Tests for get_number_of_property_paths_for_node_shape function."""
    
    def test_returns_path_count(self, mock_sparql_executor):
        """Test that function returns count of property paths."""
        mock_sparql_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"pathCount": {"value": "7"}}
                ]
            }
        }
        
        result = get_number_of_property_paths_for_node_shape(
            "http://ex.org/PersonShape",
            executor=mock_sparql_executor
        )
        
        assert result == 7
    
    def test_node_shape_with_no_paths(self, mock_sparql_executor):
        """Test node shape with no property paths."""
        mock_sparql_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"pathCount": {"value": "0"}}
                ]
            }
        }
        
        result = get_number_of_property_paths_for_node_shape(
            "http://ex.org/EmptyShape",
            executor=mock_sparql_executor
        )
        
        assert result == 0


class TestGetNumberOfConstraintsForNodeShape:
    """Tests for get_number_of_constraints_for_node_shape function."""
    
    def test_returns_constraint_count(self, mock_sparql_executor):
        """Test that function returns count of constraints."""
        # Mock two queries: first for property shapes, second for constraint count
        mock_sparql_executor.execute_query.side_effect = [
            # First call: property shapes query
            {
                "results": {
                    "bindings": [
                        {"propertyShape": {"value": "http://ex.org/Prop1"}},
                        {"propertyShape": {"value": "http://ex.org/Prop2"}}
                    ]
                }
            },
            # Second call: constraint count query
            {
                "results": {
                    "bindings": [
                        {"constraintCount": {"value": "15"}}
                    ]
                }
            }
        ]
        
        result = get_number_of_constraints_for_node_shape(
            "http://ex.org/PersonShape",
            executor=mock_sparql_executor
        )
        
        assert result == 15
    
    def test_node_shape_with_no_constraints(self, mock_sparql_executor):
        """Test node shape with no constraints."""
        mock_sparql_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = get_number_of_constraints_for_node_shape(
            "http://ex.org/SimpleShape",
            executor=mock_sparql_executor
        )
        
        assert result == 0
