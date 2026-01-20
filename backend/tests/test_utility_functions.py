"""
Unit tests for utility_functions module.
Tests for utility functions like prefix extraction and RDF list parsing.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from functions.utility_functions import (
    get_prefixes_from_endpoint,
    parse_rdf_list,
    benchmark_function_execution
)


class TestGetPrefixesFromEndpoint:
    """Test get_prefixes_from_endpoint function"""
    
    @patch('functions.prefix_utils.extract_prefixes_from_sparql_graphs')
    def test_extracts_prefixes_successfully(self, mock_extract):
        """Should extract prefixes from SPARQL endpoint"""
        mock_extract.return_value = {
            'sh': 'http://www.w3.org/ns/shacl#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'ex': 'http://example.org/'
        }
        
        result = get_prefixes_from_endpoint("http://localhost:8890/sparql")
        
        assert 'sh' in result
        assert 'rdf' in result
        assert 'ex' in result
        assert result['ex'] == 'http://example.org/'
    
    @patch('functions.prefix_utils.extract_prefixes_from_sparql_graphs')
    def test_returns_fallback_on_extraction_error(self, mock_extract):
        """Should return fallback prefixes when extraction fails"""
        mock_extract.side_effect = Exception("Connection error")
        
        result = get_prefixes_from_endpoint("http://localhost:8890/sparql")
        
        assert 'sh' in result
        assert 'rdf' in result
        assert 'rdfs' in result
        assert 'shs' in result
    
    @patch('functions.prefix_utils.extract_prefixes_from_sparql_graphs')
    def test_fallback_prefixes_have_correct_namespaces(self, mock_extract):
        """Should have correct namespace URIs in fallback"""
        mock_extract.side_effect = Exception("Error")
        
        result = get_prefixes_from_endpoint("http://localhost:8890/sparql")
        
        assert result['sh'] == 'http://www.w3.org/ns/shacl#'
        assert result['rdf'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        assert result['rdfs'] == 'http://www.w3.org/2000/01/rdf-schema#'


class TestParseRdfList:
    """Test parse_rdf_list function"""
    
    def test_extracts_items_from_rdf_list(self):
        """Should extract all items from RDF list"""
        mock_executor = Mock()
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"item": {"value": "http://example.org/item1"}},
                    {"item": {"value": "http://example.org/item2"}},
                    {"item": {"value": "http://example.org/item3"}}
                ]
            }
        }
        
        result = parse_rdf_list(
            "http://example.org/list",
            "http://example.org/shapes",
            executor=mock_executor
        )
        
        assert len(result) == 3
        assert "http://example.org/item1" in result
        assert "http://example.org/item2" in result
        assert "http://example.org/item3" in result
    
    def test_returns_empty_list_for_no_items(self):
        """Should return empty list when RDF list is empty"""
        mock_executor = Mock()
        mock_executor.execute_query.return_value = {
            "results": {"bindings": []}
        }
        
        result = parse_rdf_list(
            "http://example.org/emptylist",
            "http://example.org/shapes",
            executor=mock_executor
        )
        
        assert result == []
    
    def test_uses_default_executor_when_none_provided(self):
        """Should use default executor when not provided"""
        with patch('functions.utility_functions.get_default_executor') as mock_get_default:
            mock_executor = Mock()
            mock_executor.execute_query.return_value = {
                "results": {"bindings": []}
            }
            mock_get_default.return_value = mock_executor
            
            result = parse_rdf_list(
                "http://example.org/list",
                "http://example.org/shapes"
            )
            
            mock_get_default.assert_called_once()
            assert result == []
    
    def test_preserves_item_order(self):
        """Should preserve the order of items in RDF list"""
        mock_executor = Mock()
        mock_executor.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"item": {"value": "first"}},
                    {"item": {"value": "second"}},
                    {"item": {"value": "third"}}
                ]
            }
        }
        
        result = parse_rdf_list(
            "http://example.org/list",
            "http://example.org/shapes",
            executor=mock_executor
        )
        
        assert result == ["first", "second", "third"]


class TestBenchmarkFunctionExecution:
    """Test benchmark_function_execution function"""
    
    @patch('functions.utility_functions.csv')
    @patch('builtins.open', create=True)
    def test_benchmarks_function(self, mock_open, mock_csv):
        """Should benchmark function execution"""
        test_func = Mock(return_value="result")
        
        result = benchmark_function_execution(test_func, runs=3, csv_filename="test.csv")
        
        assert 'average_ms' in result
        assert 'times_ms' in result
        assert 'results' in result
        assert len(result['results']) == 3
        assert test_func.call_count == 3
    
    @patch('functions.utility_functions.csv')
    @patch('builtins.open', create=True)
    def test_measures_time_in_milliseconds(self, mock_open, mock_csv):
        """Should measure time in milliseconds"""
        import time
        def slow_func():
            time.sleep(0.01)  # 10ms
            return "done"
        
        result = benchmark_function_execution(slow_func, runs=2, csv_filename="test.csv")
        
        assert result['average_ms'] > 0
        assert len(result['times_ms']) == 2
    
    @patch('functions.utility_functions.csv')
    @patch('builtins.open', create=True)
    def test_calculates_correct_average(self, mock_open, mock_csv):
        """Should calculate correct average time"""
        test_func = Mock(return_value="result")
        
        result = benchmark_function_execution(test_func, runs=5, csv_filename="test.csv")
        
        assert len(result['results']) == 5
        assert 'average_ms' in result
        assert result['average_ms'] >= 0
    
    @patch('functions.utility_functions.csv')
    @patch('builtins.open', create=True)
    def test_handles_function_with_return_value(self, mock_open, mock_csv):
        """Should handle functions that return values"""
        test_func = Mock(return_value=42)
        
        result = benchmark_function_execution(test_func, runs=1, csv_filename="test.csv")
        
        assert 'average_ms' in result
        assert result['results'][0] == 42
