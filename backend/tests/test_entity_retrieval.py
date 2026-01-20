"""
Unit tests for entity_retrieval module.
Tests for entity retrieval functions.
"""
import pytest
from unittest.mock import Mock, patch
from functions.entity_retrieval import (
    get_all_shapes_names,
    get_all_focus_node_names,
    get_all_property_path_names,
    get_all_constraint_components_names,
    get_violations_for_shape_name,
    get_number_of_shapes_in_shapes_graph,
    get_number_of_violations_in_validation_report
)


@pytest.fixture
def mock_executor():
    """Create mock SPARQL executor"""
    executor = Mock()
    return executor


class TestGetAllShapesNames:
    """Test get_all_shapes_names function"""
    
    def test_returns_shape_names(self, mock_executor):
        """Should return list of shape names"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"shape": {"value": "http://example.org/Shape1"}},
                    {"shape": {"value": "http://example.org/Shape2"}}
                ]
            }
        }
        
        result = get_all_shapes_names(
            graph_uri="http://test.org/graph",
            executor=mock_executor
        )
        
        assert len(result) == 2
        assert "http://example.org/Shape1" in result
        assert "http://example.org/Shape2" in result
    
    def test_returns_empty_list_when_no_shapes(self, mock_executor):
        """Should return empty list when no shapes found"""
        mock_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = get_all_shapes_names(executor=mock_executor)
        
        assert result == []
    
    def test_executes_sparql_query(self, mock_executor):
        """Should execute SPARQL query"""
        mock_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        get_all_shapes_names(executor=mock_executor)
        
        assert mock_executor.execute_query.called
        call_args = mock_executor.execute_query.call_args
        assert "SELECT DISTINCT ?shape" in call_args[0][0]


class TestGetAllFocusNodeNames:
    """Test get_all_focus_node_names function"""
    
    def test_returns_focus_node_names(self, mock_executor):
        """Should return list of focus node names"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"focusNode": {"value": "http://example.org/Node1"}},
                    {"focusNode": {"value": "http://example.org/Node2"}}
                ]
            }
        }
        
        result = get_all_focus_node_names(executor=mock_executor)
        
        assert len(result) == 2
        assert "http://example.org/Node1" in result
    
    def test_handles_empty_results(self, mock_executor):
        """Should handle empty results"""
        mock_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = get_all_focus_node_names(executor=mock_executor)
        
        assert result == []


class TestGetAllPropertyPathNames:
    """Test get_all_property_path_names function"""
    
    def test_returns_property_paths(self, mock_executor):
        """Should return list of property paths"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"propertyPath": {"value": "http://example.org/property1"}},
                    {"propertyPath": {"value": "http://example.org/property2"}}
                ]
            }
        }
        
        result = get_all_property_path_names(executor=mock_executor)
        
        assert len(result) == 2
        assert "http://example.org/property1" in result


class TestGetAllConstraintComponentsNames:
    """Test get_all_constraint_components_names function"""
    
    def test_returns_constraint_components(self, mock_executor):
        """Should return list of constraint components"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"constraintComponent": {"value": "http://www.w3.org/ns/shacl#MinCountConstraintComponent"}},
                    {"constraintComponent": {"value": "http://www.w3.org/ns/shacl#MaxCountConstraintComponent"}}
                ]
            }
        }
        
        result = get_all_constraint_components_names(executor=mock_executor)
        
        assert len(result) == 2
        assert any("MinCount" in c for c in result)


class TestGetViolationsForShapeName:
    """Test get_violations_for_shape_name function"""
    
    def test_returns_violations(self, mock_executor):
        """Should return violations for shape"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "focusNode": {"value": "http://example.org/Node1"},
                        "resultMessage": {"value": "Validation failed"},
                        "resultPath": {"value": "http://example.org/prop"},
                        "resultSeverity": {"value": "http://www.w3.org/ns/shacl#Violation"},
                        "constraintComponent": {"value": "http://www.w3.org/ns/shacl#MinCountConstraintComponent"}
                    }
                ]
            }
        }
        
        result = get_violations_for_shape_name(
            shape_name="http://example.org/Shape1",
            executor=mock_executor
        )
        
        assert len(result) == 1
        assert result[0]["focusNode"] == "http://example.org/Node1"


class TestGetNumberOfShapesInShapesGraph:
    """Test get_number_of_shapes_in_shapes_graph function"""
    
    def test_returns_count(self, mock_executor):
        """Should return count of shapes"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "nodeShapesCount": {"value": "5"},
                        "propertyShapesCount": {"value": "10"}
                    }
                ]
            }
        }
        
        result = get_number_of_shapes_in_shapes_graph(executor=mock_executor)
        
        assert result == {"nodeShapes": 5, "propertyShapes": 10}
    
    def test_handles_zero_shapes(self, mock_executor):
        """Should handle zero shapes"""
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "nodeShapesCount": {"value": "0"},
                        "propertyShapesCount": {"value": "0"}
                    }
                ]
            }
        }
        
        result = get_number_of_shapes_in_shapes_graph(executor=mock_executor)
        
        assert result == {"nodeShapes": 0, "propertyShapes": 0}


class TestGetNumberOfViolationsInValidationReport:
    """Test get_number_of_violations_in_validation_report function"""
    
    def test_returns_violation_count(self, mock_executor):
        """Should return violation count"""
        mock_executor.execute_count_query.return_value = 42
        
        result = get_number_of_violations_in_validation_report(executor=mock_executor)
        
        assert result == 42
    
    def test_handles_zero_violations(self, mock_executor):
        """Should handle zero violations"""
        mock_executor.execute_count_query.return_value = 0
        
        result = get_number_of_violations_in_validation_report(executor=mock_executor)
        
        assert result == 0
