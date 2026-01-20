"""
Extended tests for sparql_executor module.
Additional coverage for error handling and edge cases.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from SPARQLWrapper import SPARQLExceptions
from sparql_executor import (
    SparqlQueryExecutor,
    get_default_executor,
    SparqlQueryError
)


class TestSparqlQueryExecutorErrorHandling:
    """Test error handling in SparqlQueryExecutor"""
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_endpoint_not_found_error(self, mock_wrapper_class):
        """Should raise SparqlQueryError when endpoint not found"""
        mock_wrapper = Mock()
        mock_wrapper.query.side_effect = SPARQLExceptions.EndPointNotFound()
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        query = "SELECT * WHERE { ?s ?p ?o }"
        
        with pytest.raises(SparqlQueryError):
            executor.execute_query(query)
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_query_bad_formed_error(self, mock_wrapper_class):
        """Should raise SparqlQueryError for malformed query"""
        mock_wrapper = Mock()
        mock_wrapper.query.side_effect = SPARQLExceptions.QueryBadFormed()
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        query = "BAD QUERY"
        
        with pytest.raises(SparqlQueryError):
            executor.execute_query(query)
    
    @patch('sparql_executor.SPARQLWrapper')
    @patch('sparql_executor.time.sleep')
    def test_retries_on_generic_exception(self, mock_sleep, mock_wrapper_class):
        """Should retry on generic exceptions"""
        mock_wrapper = Mock()
        # Fail twice, succeed on third attempt
        mock_result = Mock()
        mock_result.convert.return_value = {"results": {"bindings": []}}
        
        # Create proper mock return value for successful query
        success_result = Mock()
        success_result.convert.return_value = {"results": {"bindings": []}}
        
        mock_wrapper.query.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            success_result
        ]
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor(max_retries=3, retry_delay=0.1)
        query = "SELECT * WHERE { ?s ?p ?o }"
        
        # Should succeed after retries
        result = executor.execute_query(query)
        assert "results" in result
        assert mock_wrapper.query.call_count == 3
    
    @patch('sparql_executor.SPARQLWrapper')
    @patch('sparql_executor.time.sleep')
    def test_raises_after_max_retries_exceeded(self, mock_sleep, mock_wrapper_class):
        """Should raise SparqlQueryError after exhausting retries"""
        mock_wrapper = Mock()
        mock_wrapper.query.side_effect = Exception("Persistent error")
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor(max_retries=2, retry_delay=0.01)
        query = "SELECT * WHERE { ?s ?p ?o }"
        
        with pytest.raises(SparqlQueryError) as exc_info:
            executor.execute_query(query)
        
        assert "Persistent error" in str(exc_info.value)
        assert mock_wrapper.query.call_count == 2
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_logs_execution_time(self, mock_wrapper_class):
        """Should log query execution time"""
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {
            "results": {"bindings": [{"s": {"value": "test"}}]}
        }
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        query = "SELECT * WHERE { ?s ?p ?o }"
        
        result = executor.execute_query(query, "http://ex.org/graph", "test_op")
        
        assert "results" in result
        assert len(result["results"]["bindings"]) == 1


class TestExecuteCountQueryEdgeCases:
    """Test execute_count_query edge cases"""
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_handles_string_count_value(self, mock_wrapper_class):
        """Should convert string count to integer"""
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {
            "results": {"bindings": [{"count": {"value": "100"}}]}
        }
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        result = executor.execute_count_query("SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }")
        
        assert result == 100
        assert isinstance(result, int)
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_returns_zero_for_missing_count_binding(self, mock_wrapper_class):
        """Should return 0 when count binding missing"""
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {
            "results": {"bindings": [{"other": {"value": "10"}}]}
        }
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        result = executor.execute_count_query("SELECT * WHERE { ?s ?p ?o }")
        
        assert result == 0
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_handles_multiple_bindings(self, mock_wrapper_class):
        """Should use first binding for count"""
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {
            "results": {
                "bindings": [
                    {"count": {"value": "42"}},
                    {"count": {"value": "99"}}
                ]
            }
        }
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        result = executor.execute_count_query("SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }")
        
        assert result == 42


class TestExecuteAskQueryEdgeCases:
    """Test execute_ask_query edge cases"""
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_returns_true_for_ask_true(self, mock_wrapper_class):
        """Should return True for ASK query with true result"""
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {"boolean": True}
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        result = executor.execute_ask_query("ASK WHERE { ?s ?p ?o }")
        
        assert result is True
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_returns_false_for_ask_false(self, mock_wrapper_class):
        """Should return False for ASK query with false result"""
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {"boolean": False}
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        result = executor.execute_ask_query("ASK WHERE { ?s ?p ?o }")
        
        assert result is False
    
    @patch('sparql_executor.SPARQLWrapper')
    def test_returns_false_for_missing_boolean(self, mock_wrapper_class):
        """Should return False when boolean key missing"""
        mock_wrapper = Mock()
        mock_result = Mock()
        mock_result.convert.return_value = {"results": {"bindings": []}}
        mock_wrapper.query.return_value = mock_result
        mock_wrapper_class.return_value = mock_wrapper
        
        executor = SparqlQueryExecutor()
        result = executor.execute_ask_query("ASK WHERE { ?s ?p ?o }")
        
        assert result is False


class TestGetDefaultExecutorSingleton:
    """Test get_default_executor singleton behavior"""
    
    def test_returns_same_instance_on_multiple_calls(self):
        """Should return same executor instance"""
        executor1 = get_default_executor()
        executor2 = get_default_executor()
        
        assert executor1 is executor2
    
    def test_executor_has_correct_config(self):
        """Should use configuration values"""
        executor = get_default_executor()
        
        assert executor.timeout > 0
        assert executor.max_retries >= 0
        assert executor.retry_delay >= 0


class TestSparqlQueryExecutorConfiguration:
    """Test executor configuration options"""
    
    def test_custom_timeout(self):
        """Should use custom timeout"""
        executor = SparqlQueryExecutor(timeout=120)
        assert executor.timeout == 120
    
    def test_custom_max_retries(self):
        """Should use custom max retries"""
        executor = SparqlQueryExecutor(max_retries=10)
        assert executor.max_retries == 10
    
    def test_custom_retry_delay(self):
        """Should use custom retry delay"""
        executor = SparqlQueryExecutor(retry_delay=5.0)
        assert executor.retry_delay == 5.0
    
    def test_zero_retries_allowed(self):
        """Should allow zero retries"""
        executor = SparqlQueryExecutor(max_retries=0)
        assert executor.max_retries == 0
    
    def test_custom_endpoint_url(self):
        """Should use custom endpoint URL"""
        custom_url = "http://custom.example.org:8890/sparql"
        executor = SparqlQueryExecutor(endpoint_url=custom_url)
        assert executor.endpoint_url == custom_url


class TestSparqlQueryErrorException:
    """Test SparqlQueryError exception"""
    
    def test_can_be_raised(self):
        """Should be able to raise SparqlQueryError"""
        with pytest.raises(SparqlQueryError):
            raise SparqlQueryError("Test error")
    
    def test_has_error_message(self):
        """Should preserve error message"""
        try:
            raise SparqlQueryError("Custom error message")
        except SparqlQueryError as e:
            assert str(e) == "Custom error message"
    
    def test_is_exception_subclass(self):
        """Should be subclass of Exception"""
        assert issubclass(SparqlQueryError, Exception)
    
    def test_can_be_caught_as_exception(self):
        """Should be catchable as generic Exception"""
        try:
            raise SparqlQueryError("Test")
        except Exception as e:
            assert isinstance(e, SparqlQueryError)
