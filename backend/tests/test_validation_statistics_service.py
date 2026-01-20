"""
Unit Tests for validation_statistics_service.py

Tests for basic statistical functions that query counts and metrics from
SHACL validation reports and shapes graphs.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from functions.validation_statistics_service import (
    get_number_of_violations_in_validation_report,
    get_number_of_node_shapes,
    get_number_of_node_shapes_with_violations,
    get_number_of_paths_in_shapes_graph,
    get_number_of_paths_with_violations,
    get_number_of_focus_nodes_in_validation_report,
    count_triples
)
from validators import ValidationError


class TestGetNumberOfViolations:
    """Tests for get_number_of_violations_in_validation_report function."""
    
    def test_returns_violation_count(self, mock_sparql_executor):
        """Test that function returns the violation count."""
        mock_sparql_executor.execute_count_query.return_value = 42
        
        result = get_number_of_violations_in_validation_report(
            "http://ex.org/ValidationReport",
            executor=mock_sparql_executor
        )
        
        assert result == 42
        mock_sparql_executor.execute_count_query.assert_called_once()
    
    def test_uses_default_graph_uri(self, mock_sparql_executor):
        """Test that function uses default graph URI when not provided."""
        mock_sparql_executor.execute_count_query.return_value = 10
        
        result = get_number_of_violations_in_validation_report(
            executor=mock_sparql_executor
        )
        
        assert result == 10
    
    def test_invalid_graph_uri_raises_error(self, mock_sparql_executor):
        """Test that invalid graph URI raises ValidationError."""
        with pytest.raises(ValidationError):
            get_number_of_violations_in_validation_report(
                "invalid-uri",
                executor=mock_sparql_executor
            )
    
    def test_sparql_injection_blocked(self, mock_sparql_executor):
        """Test that SPARQL injection attempts are blocked."""
        with pytest.raises(ValidationError) as exc_info:
            get_number_of_violations_in_validation_report(
                "http://ex.org/'; DROP GRAPH",
                executor=mock_sparql_executor
            )
        assert "sparql" in str(exc_info.value).lower()
    
    def test_zero_violations(self, mock_sparql_executor):
        """Test handling of zero violations."""
        mock_sparql_executor.execute_count_query.return_value = 0
        
        result = get_number_of_violations_in_validation_report(
            "http://ex.org/ValidationReport",
            executor=mock_sparql_executor
        )
        
        assert result == 0


class TestGetNumberOfNodeShapes:
    """Tests for get_number_of_node_shapes function."""
    
    def test_returns_node_shape_count(self, mock_sparql_executor):
        """Test that function returns the node shape count."""
        mock_sparql_executor.execute_count_query.return_value = 15
        
        result = get_number_of_node_shapes(
            "http://ex.org/ShapesGraph",
            executor=mock_sparql_executor
        )
        
        assert result == 15
    
    def test_uses_default_graph_uri(self, mock_sparql_executor):
        """Test that function uses default graph URI."""
        mock_sparql_executor.execute_count_query.return_value = 5
        
        result = get_number_of_node_shapes(executor=mock_sparql_executor)
        
        assert result == 5
    
    def test_invalid_graph_uri_raises_error(self, mock_sparql_executor):
        """Test that invalid graph URI raises ValidationError."""
        with pytest.raises(ValidationError):
            get_number_of_node_shapes(
                "not-a-valid-uri",
                executor=mock_sparql_executor
            )
    
    def test_empty_shapes_graph(self, mock_sparql_executor):
        """Test handling of empty shapes graph."""
        mock_sparql_executor.execute_count_query.return_value = 0
        
        result = get_number_of_node_shapes(
            "http://ex.org/EmptyGraph",
            executor=mock_sparql_executor
        )
        
        assert result == 0


class TestGetNumberOfNodeShapesWithViolations:
    """Tests for get_number_of_node_shapes_with_violations function."""
    
    def test_returns_count_of_shapes_with_violations(self, mock_sparql_executor):
        """Test that function returns count of node shapes with violations."""
        mock_sparql_executor.execute_count_query.return_value = 8
        
        result = get_number_of_node_shapes_with_violations(
            "http://ex.org/ShapesGraph",
            "http://ex.org/ValidationReport",
            executor=mock_sparql_executor
        )
        
        assert result == 8
    
    def test_both_uris_validated(self, mock_sparql_executor):
        """Test that both graph URIs are validated."""
        # Invalid shapes graph URI
        with pytest.raises(ValidationError):
            get_number_of_node_shapes_with_violations(
                "invalid",
                "http://ex.org/ValidationReport",
                executor=mock_sparql_executor
            )
        
        # Invalid validation report URI
        with pytest.raises(ValidationError):
            get_number_of_node_shapes_with_violations(
                "http://ex.org/ShapesGraph",
                "invalid",
                executor=mock_sparql_executor
            )
    
    def test_no_violations(self, mock_sparql_executor):
        """Test handling when no shapes have violations."""
        mock_sparql_executor.execute_count_query.return_value = 0
        
        result = get_number_of_node_shapes_with_violations(
            executor=mock_sparql_executor
        )
        
        assert result == 0


class TestGetNumberOfPathsInShapesGraph:
    """Tests for get_number_of_paths_in_shapes_graph function."""
    
    def test_returns_path_count(self, mock_sparql_executor):
        """Test that function returns the path count."""
        mock_sparql_executor.execute_count_query.return_value = 25
        
        result = get_number_of_paths_in_shapes_graph(
            "http://ex.org/ShapesGraph",
            executor=mock_sparql_executor
        )
        
        assert result == 25
    
    def test_invalid_uri_rejected(self, mock_sparql_executor):
        """Test that invalid URIs are rejected."""
        with pytest.raises(ValidationError):
            get_number_of_paths_in_shapes_graph(
                "ftp://invalid.com",
                executor=mock_sparql_executor
            )
    
    def test_zero_paths(self, mock_sparql_executor):
        """Test handling of graph with no paths."""
        mock_sparql_executor.execute_count_query.return_value = 0
        
        result = get_number_of_paths_in_shapes_graph(
            "http://ex.org/EmptyGraph",
            executor=mock_sparql_executor
        )
        
        assert result == 0


class TestGetNumberOfPathsWithViolations:
    """Tests for get_number_of_paths_with_violations function."""
    
    def test_returns_count(self, mock_sparql_executor):
        """Test that function returns count of paths with violations."""
        mock_sparql_executor.execute_count_query.return_value = 12
        
        result = get_number_of_paths_with_violations(
            "http://ex.org/ValidationReport",
            executor=mock_sparql_executor
        )
        
        assert result == 12
    
    def test_uses_default_uri(self, mock_sparql_executor):
        """Test that function uses default URI."""
        mock_sparql_executor.execute_count_query.return_value = 5
        
        result = get_number_of_paths_with_violations(
            executor=mock_sparql_executor
        )
        
        assert result == 5


class TestGetNumberOfFocusNodesInValidationReport:
    """Tests for get_number_of_focus_nodes_in_validation_report function."""
    
    def test_returns_focus_node_count(self, mock_sparql_executor):
        """Test that function returns focus node count."""
        mock_sparql_executor.execute_count_query.return_value = 100
        
        result = get_number_of_focus_nodes_in_validation_report(
            "http://ex.org/ValidationReport",
            executor=mock_sparql_executor
        )
        
        assert result == 100
    
    def test_empty_report(self, mock_sparql_executor):
        """Test handling of empty validation report."""
        mock_sparql_executor.execute_count_query.return_value = 0
        
        result = get_number_of_focus_nodes_in_validation_report(
            executor=mock_sparql_executor
        )
        
        assert result == 0


class TestCountTriples:
    """Tests for count_triples function."""
    
    def test_returns_triple_count(self, mock_sparql_executor):
        """Test that function returns triple count."""
        mock_sparql_executor.execute_count_query.return_value = 5000
        
        result = count_triples(
            "http://ex.org/ValidationReport",
            executor=mock_sparql_executor
        )
        
        assert result == 5000
    
    def test_empty_graph(self, mock_sparql_executor):
        """Test handling of empty graph."""
        mock_sparql_executor.execute_count_query.return_value = 0
        
        result = count_triples(
            "http://ex.org/EmptyGraph",
            executor=mock_sparql_executor
        )
        
        assert result == 0
