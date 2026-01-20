"""
Unit tests for shape_statistics module.
Tests for statistical calculation functions.
"""
import pytest
from unittest.mock import Mock, patch
from functions.shape_statistics import (
    get_maximum_number_of_violations_in_validation_report_for_node_shape,
    get_average_number_of_violations_in_validation_report_for_node_shape,
    get_node_shape_with_most_unique_constraints
)
from config import ENDPOINT_URL


class TestGetMaximumNumberOfViolations:
    """Test get_maximum_number_of_violations_in_validation_report_for_node_shape function"""
    
    def test_returns_node_shape_with_max_violations(self):
        """Should return node shape with maximum violations"""
        mock_executor = Mock()
        
        # Mock the node shapes query
        mock_executor.execute_query.side_effect = [
            # First call: get node shapes and property shapes
            {
                "results": {
                    "bindings": [
                        {
                            "nodeShape": {"value": "http://example.org/NodeShape1"},
                            "propertyShape": {"value": "http://example.org/PS1"}
                        },
                        {
                            "nodeShape": {"value": "http://example.org/NodeShape2"},
                            "propertyShape": {"value": "http://example.org/PS2"}
                        }
                    ]
                }
            },
            # Second call: violations for NodeShape1
            {
                "results": {
                    "bindings": [
                        {"violationCount": {"value": "10"}}
                    ]
                }
            },
            # Third call: violations for NodeShape2
            {
                "results": {
                    "bindings": [
                        {"violationCount": {"value": "25"}}
                    ]
                }
            }
        ]
        
        result = get_maximum_number_of_violations_in_validation_report_for_node_shape(
            executor=mock_executor
        )
        
        assert result["nodeShape"] == "http://example.org/NodeShape2"
        assert result["violationCount"] == 25
    
    def test_handles_no_violations(self):
        """Should handle node shapes with no violations"""
        mock_executor = Mock()
        
        mock_executor.execute_query.side_effect = [
            # Node shapes query
            {
                "results": {
                    "bindings": [
                        {
                            "nodeShape": {"value": "http://example.org/NodeShape1"},
                            "propertyShape": {"value": "http://example.org/PS1"}
                        }
                    ]
                }
            },
            # Violations count (zero)
            {
                "results": {
                    "bindings": [
                        {"violationCount": {"value": "0"}}
                    ]
                }
            }
        ]
        
        result = get_maximum_number_of_violations_in_validation_report_for_node_shape(
            executor=mock_executor
        )
        
        assert result["nodeShape"] == "http://example.org/NodeShape1"
        assert result["violationCount"] == 0
    
    def test_uses_default_executor(self):
        """Should use default executor when none provided"""
        with patch('functions.shape_statistics.get_default_executor') as mock_get:
            mock_executor = Mock()
            mock_get.return_value = mock_executor
            
            # Setup mock response
            mock_executor.execute_query.side_effect = [
                {"results": {"bindings": []}},
            ]
            
            get_maximum_number_of_violations_in_validation_report_for_node_shape()
            
            mock_get.assert_called_once()


class TestGetAverageNumberOfViolations:
    """Test get_average_number_of_violations_in_validation_report_for_node_shape function"""
    
    def test_calculates_average_violations(self):
        """Should calculate average violations across node shapes"""
        mock_executor = Mock()
        
        mock_executor.execute_query.side_effect = [
            # Node shapes query
            {
                "results": {
                    "bindings": [
                        {
                            "nodeShape": {"value": "http://example.org/NS1"},
                            "propertyShape": {"value": "http://example.org/PS1"}
                        },
                        {
                            "nodeShape": {"value": "http://example.org/NS2"},
                            "propertyShape": {"value": "http://example.org/PS2"}
                        },
                        {
                            "nodeShape": {"value": "http://example.org/NS3"},
                            "propertyShape": {"value": "http://example.org/PS3"}
                        }
                    ]
                }
            },
            # Violations for NS1: 10
            {"results": {"bindings": [{"violationCount": {"value": "10"}}]}},
            # Violations for NS2: 20
            {"results": {"bindings": [{"violationCount": {"value": "20"}}]}},
            # Violations for NS3: 30
            {"results": {"bindings": [{"violationCount": {"value": "30"}}]}}
        ]
        
        result = get_average_number_of_violations_in_validation_report_for_node_shape(
            executor=mock_executor
        )
        
        # Average should be (10 + 20 + 30) / 3 = 20.0
        assert result == 20.0
    
    def test_handles_single_node_shape(self):
        """Should handle single node shape correctly"""
        mock_executor = Mock()
        
        mock_executor.execute_query.side_effect = [
            # Single node shape
            {
                "results": {
                    "bindings": [
                        {
                            "nodeShape": {"value": "http://example.org/NS1"},
                            "propertyShape": {"value": "http://example.org/PS1"}
                        }
                    ]
                }
            },
            # Violations: 42
            {"results": {"bindings": [{"violationCount": {"value": "42"}}]}}
        ]
        
        result = get_average_number_of_violations_in_validation_report_for_node_shape(
            executor=mock_executor
        )
        
        assert result == 42.0
    
    def test_returns_zero_for_no_node_shapes(self):
        """Should return 0 when no node shapes exist"""
        mock_executor = Mock()
        
        mock_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = get_average_number_of_violations_in_validation_report_for_node_shape(
            executor=mock_executor
        )
        
        assert result == 0.0


class TestGetNodeShapeWithMostUniqueConstraints:
    """Test get_node_shape_with_most_unique_constraints function"""
    
    def test_returns_shape_with_most_constraints(self):
        """Should return node shape with most unique constraints"""
        with patch('functions.shape_statistics.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "results": {
                    "bindings": [
                        {
                            "nodeShape": {"value": "http://example.org/Shape1"},
                            "numConstraints": {"value": "15"}
                        }
                    ]
                }
            }
            mock_get.return_value = mock_response
            
            result = get_node_shape_with_most_unique_constraints()
            
            assert result["nodeShape"] == "http://example.org/Shape1"
            assert result["uniqueConstraintsCount"] == 15
    
    def test_handles_tie_returns_first(self):
        """Should return first shape when there's a tie"""
        with patch('functions.shape_statistics.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "results": {
                    "bindings": [
                        {
                            "nodeShape": {"value": "http://example.org/ShapeA"},
                            "numConstraints": {"value": "10"}
                        }
                    ]
                }
            }
            mock_get.return_value = mock_response
            
            result = get_node_shape_with_most_unique_constraints()
            
            assert result["nodeShape"] == "http://example.org/ShapeA"
            assert result["uniqueConstraintsCount"] == 10
    
    def test_returns_none_when_no_shapes(self):
        """Should return None nodeShape when no shapes found"""
        with patch('functions.shape_statistics.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "results": {"bindings": []}
            }
            mock_get.return_value = mock_response
            
            result = get_node_shape_with_most_unique_constraints()
            
            assert result["nodeShape"] is None
            assert result["uniqueConstraintsCount"] == 0
    
    def test_uses_requests_library(self):
        """Should use requests to query endpoint"""
        with patch('functions.shape_statistics.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "results": {"bindings": []}
            }
            mock_get.return_value = mock_response
            
            get_node_shape_with_most_unique_constraints()
            
            assert mock_get.called
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == ENDPOINT_URL
