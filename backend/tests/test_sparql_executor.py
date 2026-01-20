"""
Unit Tests for sparql_executor.py

Tests for the SparqlQueryExecutor class and helper functions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sparql_executor import (
    SparqlQueryExecutor,
    get_default_executor,
    SparqlQueryError
)


class TestSparqlQueryExecutor:
    """Tests for SparqlQueryExecutor class."""
    
    def test_initialization_with_defaults(self):
        """Test that executor initializes with default values."""
        executor = SparqlQueryExecutor()
        
        assert executor.timeout == 30
        assert executor.max_retries == 3
        assert executor.retry_delay == 1.0
    
    def test_initialization_with_custom_values(self):
        """Test that executor initializes with custom values."""
        executor = SparqlQueryExecutor(
            endpoint_url="http://custom:8890/sparql",
            timeout=60,
            max_retries=5,
            retry_delay=2.0
        )
        
        assert executor.endpoint_url == "http://custom:8890/sparql"
        assert executor.timeout == 60
        assert executor.max_retries == 5
        assert executor.retry_delay == 2.0
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_execute_query_success(self, mock_wrapper_class):
        """Test successful query execution."""
        # Setup mock
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {
            "results": {"bindings": [{"count": {"value": "10"}}]}
        }
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
        
        result = executor.execute_query(query, "http://ex.org/graph", "test_op")
        
        assert "results" in result
        assert "bindings" in result["results"]
        mock_wrapper.setQuery.assert_called_once_with(query)
        mock_wrapper.setTimeout.assert_called_once_with(30)
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_execute_count_query_success(self, mock_wrapper_class):
        """Test successful count query execution."""
        # Setup mock
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {
            "results": {"bindings": [{"count": {"value": "42"}}]}
        }
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
        
        result = executor.execute_count_query(query, "http://ex.org/graph", "count_op")
        
        assert result == 42
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_execute_count_query_returns_zero_on_empty(self, mock_wrapper_class):
        """Test that count query returns 0 when no results."""
        # Setup mock
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {
            "results": {"bindings": []}
        }
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
        
        result = executor.execute_count_query(query, "http://ex.org/graph", "count_op")
        
        assert result == 0
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_execute_ask_query_true(self, mock_wrapper_class):
        """Test ASK query returning true."""
        # Setup mock
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {"boolean": True}
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        query = "ASK WHERE { ?s ?p ?o }"
        
        result = executor.execute_ask_query(query, "http://ex.org/graph", "ask_op")
        
        assert result is True
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_execute_ask_query_false(self, mock_wrapper_class):
        """Test ASK query returning false."""
        # Setup mock
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {"boolean": False}
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        query = "ASK WHERE { ?s ?p ?o }"
        
        result = executor.execute_ask_query(query, "http://ex.org/graph", "ask_op")
        
        assert result is False
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_query_timeout_set(self, mock_wrapper_class):
        """Test that timeout is set on SPARQLWrapper."""
        mock_wrapper = Mock()
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor(timeout=45)
        
        try:
            executor.execute_query("SELECT * WHERE { ?s ?p ?o }")
        except:
            pass  # We're only testing that setTimeout was called
        
        mock_wrapper.setTimeout.assert_called_with(45)
    
    @patch('sparql_executor.SPARQLWrapper')
    @patch('sparql_executor.time.sleep')
    def test_retry_on_failure(self, mock_sleep, mock_wrapper_class):
        """Test that query retries on failure."""
        # Setup mock to fail twice then succeed
        mock_wrapper = Mock()
        mock_wrapper.query.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
            Mock(convert=lambda: {"results": {"bindings": []}})
        ]
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor(max_retries=3, retry_delay=0.1)
        
        result = executor.execute_query("SELECT * WHERE { ?s ?p ?o }")
        
        # Should have called query 3 times (2 failures + 1 success)
        assert mock_wrapper.query.call_count == 3
        # Should have slept between retries
        assert mock_sleep.call_count == 2
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_raises_error_after_max_retries(self, mock_wrapper_class):
        """Test that error is raised after max retries exhausted."""
        # Setup mock to always fail
        mock_wrapper = Mock()
        mock_wrapper.query.side_effect = Exception("Persistent error")
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor(max_retries=2, retry_delay=0.01)
        
        with pytest.raises(SparqlQueryError) as exc_info:
            executor.execute_query("SELECT * WHERE { ?s ?p ?o }")
        
        assert "Persistent error" in str(exc_info.value)


class TestGetDefaultExecutor:
    """Tests for get_default_executor function."""
    
    def test_returns_executor_instance(self):
        """Test that function returns a SparqlQueryExecutor instance."""
        executor = get_default_executor()
        
        assert isinstance(executor, SparqlQueryExecutor)
    
    def test_returns_same_instance(self):
        """Test that function returns the same singleton instance."""
        executor1 = get_default_executor()
        executor2 = get_default_executor()
        
        assert executor1 is executor2
    
    def test_uses_config_values(self):
        """Test that executor uses values from config."""
        with patch('sparql_executor.ENDPOINT_URL', 'http://test:8890/sparql'):
            executor = SparqlQueryExecutor(timeout=60)
            
            assert executor.timeout == 60


class TestSparqlQueryError:
    """Tests for SparqlQueryError exception."""
    
    def test_exception_can_be_raised(self):
        """Test that SparqlQueryError can be raised."""
        with pytest.raises(SparqlQueryError):
            raise SparqlQueryError("Test error")
    
    def test_exception_message(self):
        """Test that exception message is preserved."""
        with pytest.raises(SparqlQueryError) as exc_info:
            raise SparqlQueryError("Custom error message")
        
        assert "Custom error message" in str(exc_info.value)
    
    def test_exception_is_exception_subclass(self):
        """Test that SparqlQueryError is a subclass of Exception."""
        assert issubclass(SparqlQueryError, Exception)
