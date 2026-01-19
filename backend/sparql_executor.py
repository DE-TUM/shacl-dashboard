"""
SPARQL Query Executor Module

This module provides a unified interface for executing SPARQL queries against
the configured endpoint. It abstracts the SPARQLWrapper boilerplate and provides
additional features like timeout handling, retry logic, structured logging,
and easier mocking for tests.

Key Features:
- Centralized SPARQL query execution
- Automatic timeout handling
- Retry logic with exponential backoff
- Integrated logging with execution time tracking
- Simplified error handling
- Easy to mock for unit testing

Usage:
    from sparql_executor import SparqlQueryExecutor
    
    executor = SparqlQueryExecutor()
    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
    results = executor.execute_query(query, graph_uri="http://example.org/graph")
"""

from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from typing import Dict, Any, Optional
import time
import logging
from config import ENDPOINT_URL

logger = logging.getLogger(__name__)


class SparqlQueryError(Exception):
    """Exception raised when a SPARQL query fails."""
    pass


class SparqlQueryExecutor:
    """
    Executor class for SPARQL queries with built-in retry logic, timeout handling,
    and structured logging.
    
    This class provides a clean abstraction over SPARQLWrapper, making it easier
    to execute queries consistently across the application and simplifying testing.
    
    Attributes:
        endpoint_url: The SPARQL endpoint URL to query
        timeout: Query timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts for failed queries (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 1.0)
    """
    
    def __init__(
        self,
        endpoint_url: str = ENDPOINT_URL,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the SPARQL query executor.
        
        Args:
            endpoint_url: The SPARQL endpoint URL (default: from config)
            timeout: Query timeout in seconds (default: 30)
            max_retries: Maximum retry attempts (default: 3)
            retry_delay: Initial retry delay in seconds (default: 1.0)
        """
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        logger.debug(
            "Initialized SparqlQueryExecutor",
            extra={
                'endpoint_url': endpoint_url,
                'timeout': timeout,
                'max_retries': max_retries
            }
        )
    
    def execute_query(
        self,
        query: str,
        graph_uri: Optional[str] = None,
        operation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a SPARQL query with automatic retry logic and logging.
        
        This method:
        1. Creates a SPARQLWrapper instance with the configured endpoint
        2. Sets the query and return format
        3. Executes the query with timeout and retry logic
        4. Logs execution time and query details
        5. Returns the parsed JSON results
        
        Args:
            query: The SPARQL query string to execute
            graph_uri: Optional graph URI for logging context
            operation_name: Optional name describing the operation for logging
            
        Returns:
            Dict containing the query results in JSON format
            
        Raises:
            SparqlQueryError: If the query fails after all retry attempts
            
        Example:
            executor = SparqlQueryExecutor()
            query = '''
                SELECT ?s ?p ?o
                FROM <http://example.org/graph>
                WHERE { ?s ?p ?o }
                LIMIT 10
            '''
            results = executor.execute_query(
                query,
                graph_uri="http://example.org/graph",
                operation_name="get_triples"
            )
        """
        start_time = time.time()
        attempt = 0
        last_exception = None
        
        # Log query initiation
        log_context = {
            'operation': operation_name or 'unknown',
            'graph_uri': graph_uri or 'unspecified',
            'query_length': len(query)
        }
        logger.info(f"Executing SPARQL query: {operation_name or 'query'}", extra=log_context)
        
        while attempt < self.max_retries:
            attempt += 1
            try:
                # Create and configure SPARQL wrapper
                sparql = SPARQLWrapper(self.endpoint_url)
                sparql.setTimeout(self.timeout)
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                
                # Execute query
                query_start = time.time()
                results = sparql.query().convert()
                execution_time = time.time() - query_start
                total_time = time.time() - start_time
                
                # Log successful execution
                result_count = len(results.get("results", {}).get("bindings", []))
                logger.info(
                    f"SPARQL query executed successfully",
                    extra={
                        **log_context,
                        'execution_time': round(execution_time, 3),
                        'total_time': round(total_time, 3),
                        'result_count': result_count,
                        'attempt': attempt
                    }
                )
                
                return results
                
            except SPARQLExceptions.EndPointNotFound as e:
                last_exception = e
                logger.error(
                    f"SPARQL endpoint not found: {self.endpoint_url}",
                    extra={**log_context, 'attempt': attempt, 'error_type': 'EndPointNotFound'},
                    exc_info=True
                )
                # Don't retry for endpoint not found
                break
                
            except SPARQLExceptions.QueryBadFormed as e:
                last_exception = e
                logger.error(
                    f"Malformed SPARQL query",
                    extra={
                        **log_context,
                        'attempt': attempt,
                        'error_type': 'QueryBadFormed',
                        'query_preview': query[:200] + '...' if len(query) > 200 else query
                    },
                    exc_info=True
                )
                # Don't retry for bad queries
                break
                
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"SPARQL query failed (attempt {attempt}/{self.max_retries}): {str(e)}",
                    extra={
                        **log_context,
                        'attempt': attempt,
                        'error_type': type(e).__name__,
                        'will_retry': attempt < self.max_retries
                    }
                )
                
                # If we haven't exhausted retries, wait and try again
                if attempt < self.max_retries:
                    # Exponential backoff: delay * 2^(attempt-1)
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    logger.debug(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
        
        # All retries exhausted or non-retryable error
        total_time = time.time() - start_time
        error_msg = f"SPARQL query failed after {attempt} attempt(s): {str(last_exception)}"
        
        logger.error(
            error_msg,
            extra={
                **log_context,
                'total_time': round(total_time, 3),
                'total_attempts': attempt,
                'error_type': type(last_exception).__name__ if last_exception else 'Unknown'
            }
        )
        
        raise SparqlQueryError(error_msg) from last_exception
    
    def execute_count_query(
        self,
        query: str,
        graph_uri: Optional[str] = None,
        operation_name: Optional[str] = None,
        count_var: str = "count"
    ) -> int:
        """
        Execute a SPARQL COUNT query and return the integer result.
        
        This is a convenience method for queries that return a single count value.
        
        Args:
            query: The SPARQL COUNT query string
            graph_uri: Optional graph URI for logging context
            operation_name: Optional operation name for logging
            count_var: The variable name used in the COUNT (default: "count")
            
        Returns:
            The count as an integer
            
        Raises:
            SparqlQueryError: If the query fails or doesn't return a count
            
        Example:
            executor = SparqlQueryExecutor()
            query = '''
                SELECT (COUNT(?s) AS ?count)
                FROM <http://example.org/graph>
                WHERE { ?s ?p ?o }
            '''
            count = executor.execute_count_query(query, count_var="count")
        """
        results = self.execute_query(query, graph_uri, operation_name)
        
        try:
            bindings = results["results"]["bindings"]
            if not bindings:
                logger.warning("Count query returned no results", extra={'query_preview': query[:100]})
                return 0
            
            count_value = bindings[0].get(count_var, {}).get("value", "0")
            return int(count_value)
            
        except (KeyError, IndexError, ValueError) as e:
            logger.error(
                f"Failed to extract count from query results: {str(e)}",
                extra={'error_type': type(e).__name__},
                exc_info=True
            )
            raise SparqlQueryError(f"Failed to extract count from results: {str(e)}") from e
    
    def execute_ask_query(
        self,
        query: str,
        graph_uri: Optional[str] = None,
        operation_name: Optional[str] = None
    ) -> bool:
        """
        Execute a SPARQL ASK query and return the boolean result.
        
        ASK queries return a boolean indicating whether a pattern exists.
        
        Args:
            query: The SPARQL ASK query string
            graph_uri: Optional graph URI for logging context
            operation_name: Optional operation name for logging
            
        Returns:
            True if the pattern exists, False otherwise
            
        Raises:
            SparqlQueryError: If the query fails
            
        Example:
            executor = SparqlQueryExecutor()
            query = '''
                ASK FROM <http://example.org/graph>
                WHERE { ?s a <http://example.org/Type> }
            '''
            exists = executor.execute_ask_query(query)
        """
        results = self.execute_query(query, graph_uri, operation_name)
        
        try:
            return results.get("boolean", False)
        except Exception as e:
            logger.error(
                f"Failed to extract boolean from ASK query: {str(e)}",
                extra={'error_type': type(e).__name__},
                exc_info=True
            )
            raise SparqlQueryError(f"Failed to extract boolean from ASK results: {str(e)}") from e


# Global singleton instance for convenience
_default_executor: Optional[SparqlQueryExecutor] = None


def get_default_executor() -> SparqlQueryExecutor:
    """
    Get the default global SparqlQueryExecutor instance.
    
    This provides a singleton executor for use across the application.
    Useful for simple cases where custom configuration isn't needed.
    
    Returns:
        The default SparqlQueryExecutor instance
        
    Example:
        from sparql_executor import get_default_executor
        
        executor = get_default_executor()
        results = executor.execute_query(query)
    """
    global _default_executor
    if _default_executor is None:
        _default_executor = SparqlQueryExecutor()
    return _default_executor
