"""
Unit tests for violation_analysis_service module.
Tests for violation analysis functions.
"""
import pytest
from unittest.mock import Mock
from functions.violation_analysis_service import (
    get_violations_per_node_shape,
    get_violations_per_path,
    get_violations_per_focus_node
)


@pytest.fixture
def mock_executor():
    """Create mock SPARQL executor"""
    executor = Mock()
    return executor


class TestGetViolationsPerNodeShape:
    """Test get_violations_per_node_shape function"""
    
    def test_returns_violations_per_shape(self, mock_executor):
        """Should return violations grouped by node shape"""
        # Mock first query - node shapes and properties
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "nodeShape": {"value": "http://example.org/NodeShape1"},
                        "propertyShape": {"value": "http://example.org/PropertyShape1"}
                    },
                    {
                        "nodeShape": {"value": "http://example.org/NodeShape1"},
                        "propertyShape": {"value": "http://example.org/PropertyShape2"}
                    }
                ]
            }
        }
        
        # Mock execute_count_query for violations
        mock_executor.execute_count_query.return_value = 8
        
        result = get_violations_per_node_shape(executor=mock_executor)
        
        assert len(result) == 1
        assert result[0]["NodeShapeName"] == "http://example.org/NodeShape1"
        assert result[0]["NumViolations"] == 8
    
    def test_handles_no_node_shapes(self, mock_executor):
        """Should handle case with no node shapes"""
        mock_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = get_violations_per_node_shape(executor=mock_executor)
        
        assert result == []
    
    def test_handles_node_shape_without_violations(self, mock_executor):
        """Should handle node shape with no violations"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "nodeShape": {"value": "http://example.org/NodeShape1"},
                        "propertyShape": {"value": "http://example.org/PropertyShape1"}
                    }
                ]
            }
        }
        
        mock_executor.execute_count_query.return_value = 0
        
        result = get_violations_per_node_shape(executor=mock_executor)
        
        assert len(result) == 1
        assert result[0]["NumViolations"] == 0


class TestGetViolationsPerPath:
    """Test get_violations_per_path function"""
    
    def test_returns_violations_per_path(self, mock_executor):
        """Should return violations grouped by path"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "path": {"value": "http://example.org/property1"},
                        "violationCount": {"value": "10"}
                    },
                    {
                        "path": {"value": "http://example.org/property2"},
                        "violationCount": {"value": "5"}
                    }
                ]
            }
        }
        
        result = get_violations_per_path(executor=mock_executor)
        
        assert len(result) == 2
        assert result[0]["PathName"] == "http://example.org/property1"
        assert result[0]["NumViolations"] == 10
        assert result[1]["NumViolations"] == 5
    
    def test_handles_no_violations(self, mock_executor):
        """Should handle no violations"""
        mock_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = get_violations_per_path(executor=mock_executor)
        
        assert result == []
    
    def test_sorts_by_violation_count(self, mock_executor):
        """Should sort results by violation count"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "path": {"value": "http://example.org/property2"},
                        "violationCount": {"value": "15"}
                    },
                    {
                        "path": {"value": "http://example.org/property3"},
                        "violationCount": {"value": "10"}
                    },
                    {
                        "path": {"value": "http://example.org/property1"},
                        "violationCount": {"value": "5"}
                    }
                ]
            }
        }
        
        result = get_violations_per_path(executor=mock_executor)
        
        # Should be sorted descending by NumViolations
        assert result[0]["NumViolations"] == 15
        assert result[1]["NumViolations"] == 10
        assert result[2]["NumViolations"] == 5


class TestGetViolationsPerFocusNode:
    """Test get_violations_per_focus_node function"""
    
    def test_returns_violations_per_focus_node(self, mock_executor):
        """Should return violations grouped by focus node"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "focusNode": {"value": "http://example.org/Node1"},
                        "violationCount": {"value": "8"}
                    },
                    {
                        "focusNode": {"value": "http://example.org/Node2"},
                        "violationCount": {"value": "3"}
                    }
                ]
            }
        }
        
        result = get_violations_per_focus_node(executor=mock_executor)
        
        assert len(result) == 2
        assert result[0]["FocusNodeName"] == "http://example.org/Node1"
        assert result[0]["NumViolations"] == 8
    
    def test_handles_empty_results(self, mock_executor):
        """Should handle empty results"""
        mock_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = get_violations_per_focus_node(executor=mock_executor)
        
        assert result == []
    
    def test_uses_correct_graph_uris(self, mock_executor):
        """Should use provided graph URIs"""
        mock_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        get_violations_per_focus_node(
            validation_report_uri="http://custom.org/report",
            executor=mock_executor
        )
        
        call_args = mock_executor.execute_query.call_args
        assert "http://custom.org/report" in call_args[0][0]
