"""
SPARQL Query Executor Module

This module provides a unified interface for executing SPARQL queries against
the configured endpoint. It abstracts the SPARQLWrapper boilerplate and provides
additional features like timeout handling, retry logic, structured logging,
caching, connection pooling, and easier mocking for tests.

Key Features:
- Centralized SPARQL query execution
- Connection pooling for better resource utilization
- Automatic timeout handling
- Retry logic with exponential backoff
- Query result caching (memory or Redis)
- Integrated logging with execution time tracking
- Simplified error handling
- Easy to mock for unit testing

Usage:
    from sparql_executor import SparqlQueryExecutor
    
    executor = SparqlQueryExecutor()
    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
    results = executor.execute_query(query, graph_uri="http://example.org/graph", use_cache=True)
"""

from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from typing import Dict, Any, Optional, List
from queue import Queue, Empty
import time
import logging
from config import ENDPOINT_URL
import threading

logger = logging.getLogger(__name__)


class SparqlQueryError(Exception):
    """Exception raised when a SPARQL query fails."""
    pass


class ConnectionPool:
    """
    Simple connection pool for SPARQLWrapper instances.
    
    Manages a pool of reusable SPARQLWrapper connections to reduce
    connection overhead and improve performance.
    """
    
    def __init__(self, endpoint_url: str, pool_size: int = 5, timeout: int = 30):
        """
        Initialize the connection pool.
        
        Args:
            endpoint_url: SPARQL endpoint URL
            pool_size: Maximum number of connections in the pool
            timeout: Connection timeout in seconds
        """
        self.endpoint_url = endpoint_url
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool: Queue = Queue(maxsize=pool_size)
        self._created_connections = 0
        self._lock = threading.Lock()
        
        logger.debug(
            "Initialized connection pool",
            extra={
                'endpoint_url': endpoint_url,
                'pool_size': pool_size,
                'timeout': timeout
            }
        )
    
    def _create_connection(self) -> SPARQLWrapper:
        """Create a new SPARQLWrapper connection."""
        sparql = SPARQLWrapper(self.endpoint_url)
        sparql.setTimeout(self.timeout)
        sparql.setReturnFormat(JSON)
        logger.debug("Created new SPARQL connection")
        return sparql
    
    def get_connection(self, wait_timeout: float = 5.0) -> SPARQLWrapper:
        """
        Get a connection from the pool.
        
        Args:
            wait_timeout: Maximum time to wait for a connection
            
        Returns:
            SPARQLWrapper instance
            
        Raises:
            TimeoutError: If no connection is available within wait_timeout
        """
        try:
            # Try to get an existing connection from the pool
            connection = self._pool.get(block=True, timeout=wait_timeout)
            logger.debug("Retrieved connection from pool")
            return connection
        except Empty:
            # Pool is empty, create a new connection if we haven't reached the limit
            with self._lock:
                if self._created_connections < self.pool_size:
                    self._created_connections += 1
                    return self._create_connection()
            
            # Pool is full and all connections are in use
            raise TimeoutError(
                f"Failed to acquire connection from pool within {wait_timeout}s. "
                f"Pool size: {self.pool_size}, all connections in use."
            )
    
    def return_connection(self, connection: SPARQLWrapper):
        """
        Return a connection to the pool.
        
        Args:
            connection: SPARQLWrapper instance to return
        """
        try:
            self._pool.put(connection, block=False)
            logger.debug("Returned connection to pool")
        except Exception as e:
            logger.warning("Failed to return connection to pool: %s", e)
    
    def close_all(self):
        """Close all connections in the pool."""
        closed_count = 0
        while not self._pool.empty():
            try:
                connection = self._pool.get(block=False)
                # SPARQLWrapper doesn't have explicit close, just let it garbage collect
                closed_count += 1
            except Empty:
                break
        
        logger.info("Closed %d connections from pool", closed_count)
        self._created_connections = 0


class SparqlQueryExecutor:
    """
    Executor class for SPARQL queries with built-in connection pooling, retry logic,
    timeout handling, and structured logging.
    
    This class provides a clean abstraction over SPARQLWrapper, making it easier
    to execute queries consistently across the application and simplifying testing.
    
    Attributes:
        endpoint_url: The SPARQL endpoint URL to query
        timeout: Query timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts for failed queries (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 1.0)
        pool_size: Connection pool size (default: 5)
        use_connection_pool: Whether to use connection pooling (default: True)
    """
    
    def __init__(
        self,
        endpoint_url: str = ENDPOINT_URL,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        pool_size: int = 5,
        use_connection_pool: bool = True
    ):
        """
        Initialize the SPARQL query executor.
        
        Args:
            endpoint_url: The SPARQL endpoint URL (default: from config)
            timeout: Query timeout in seconds (default: 30)
            max_retries: Maximum retry attempts (default: 3)
            retry_delay: Initial retry delay in seconds (default: 1.0)
            pool_size: Connection pool size (default: 5)
            use_connection_pool: Enable connection pooling (default: True)
        """
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.use_connection_pool = use_connection_pool
        
        # Initialize connection pool if enabled
        if use_connection_pool:
            self._connection_pool = ConnectionPool(
                endpoint_url=endpoint_url,
                pool_size=pool_size,
                timeout=timeout
            )
        else:
            self._connection_pool = None
        
        logger.debug(
            "Initialized SparqlQueryExecutor",
            extra={
                'endpoint_url': endpoint_url,
                'timeout': timeout,
                'max_retries': max_retries,
                'use_connection_pool': use_connection_pool,
                'pool_size': pool_size if use_connection_pool else 0
            }
        )
    
    def execute_query(
        self,
        query: str,
        graph_uri: Optional[str] = None,
        operation_name: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a SPARQL query with automatic retry logic, caching, and logging.
        
        This method:
        1. Checks cache for existing results (if caching enabled)
        2. Creates a SPARQLWrapper instance with the configured endpoint
        3. Sets the query and return format
        4. Executes the query with timeout and retry logic
        5. Caches the results (if caching enabled)
        6. Logs execution time and query details
        7. Returns the parsed JSON results
        
        Args:
            query: The SPARQL query string to execute
            graph_uri: Optional graph URI for logging context
            operation_name: Optional name describing the operation for logging
            use_cache: Whether to use caching for this query (default: True)
            cache_ttl: Optional cache TTL in seconds (default: uses cache manager's default)
            
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
                operation_name="get_triples",
                use_cache=True,
                cache_ttl=600
            )
        """
        # Check cache first (if enabled)
        if use_cache:
            try:
                from cache_manager import get_cache_manager
                cache = get_cache_manager()
                if cache.enabled:
                    cache_key = cache._generate_key(
                        operation_name or 'sparql_query',
                        query,
                        graph_uri
                    )
                    cached_result = cache.get(cache_key)
                    if cached_result is not None:
                        logger.debug(
                            "Retrieved query result from cache",
                            extra={
                                'operation': operation_name or 'unknown',
                                'cache_key': cache_key[:50] + '...'
                            }
                        )
                        return cached_result
            except Exception as e:
                logger.warning("Cache check failed, executing query: %s", e)
        
        start_time = time.time()
        attempt = 0
        last_exception = None
        
        # Log query initiation
        log_context = {
            'operation': operation_name or 'unknown',
            'graph_uri': graph_uri or 'unspecified',
            'query_length': len(query),
            'use_cache': use_cache
        }
        logger.info(f"Executing SPARQL query: {operation_name or 'query'}", extra=log_context)
        
        while attempt < self.max_retries:
            attempt += 1
            sparql = None
            try:
                # Get connection from pool or create new one
                if self.use_connection_pool and self._connection_pool:
                    sparql = self._connection_pool.get_connection()
                else:
                    sparql = SPARQLWrapper(self.endpoint_url)
                    sparql.setTimeout(self.timeout)
                    sparql.setReturnFormat(JSON)
                
                # Set query
                sparql.setQuery(query)
                
                # Execute query
                query_start = time.time()
                results = sparql.query().convert()
                execution_time = time.time() - query_start
                total_time = time.time() - start_time
                
                # Return connection to pool
                if self.use_connection_pool and self._connection_pool and sparql:
                    self._connection_pool.return_connection(sparql)
                
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
                
                # Track metrics
                try:
                    from metrics import get_metrics_manager
                    metrics = get_metrics_manager()
                    metrics.track_sparql_query(
                        operation=operation_name or 'unknown',
                        duration=execution_time,
                        success=True
                    )
                except Exception as e:
                    logger.debug("Failed to track SPARQL metrics: %s", e)
                
                # Cache the results (if enabled)
                if use_cache:
                    try:
                        from cache_manager import get_cache_manager
                        cache = get_cache_manager()
                        if cache.enabled:
                            cache_key = cache._generate_key(
                                operation_name or 'sparql_query',
                                query,
                                graph_uri
                            )
                            cache.set(cache_key, results, cache_ttl)
                            logger.debug(
                                "Cached query result",
                                extra={
                                    'operation': operation_name or 'unknown',
                                    'cache_ttl': cache_ttl or cache.default_ttl
                                }
                            )
                    except Exception as e:
                        logger.warning("Failed to cache result: %s", e)
                
                return results
                
            except SPARQLExceptions.EndPointNotFound as e:
                last_exception = e
                # Return connection to pool on error
                if self.use_connection_pool and self._connection_pool and sparql:
                    self._connection_pool.return_connection(sparql)
                
                logger.error(
                    f"SPARQL endpoint not found: {self.endpoint_url}",
                    extra={**log_context, 'attempt': attempt, 'error_type': 'EndPointNotFound'},
                    exc_info=True
                )
                # Don't retry for endpoint not found
                break
                
            except SPARQLExceptions.QueryBadFormed as e:
                last_exception = e
                # Return connection to pool on error
                if self.use_connection_pool and self._connection_pool and sparql:
                    self._connection_pool.return_connection(sparql)
                
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
                # Return connection to pool on error
                if self.use_connection_pool and self._connection_pool and sparql:
                    self._connection_pool.return_connection(sparql)
                
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
        
        # Track failed query metrics
        try:
            from metrics import get_metrics_manager
            metrics = get_metrics_manager()
            metrics.track_sparql_query(
                operation=operation_name or 'unknown',
                duration=total_time,
                success=False
            )
        except Exception as e:
            logger.debug("Failed to track SPARQL metrics: %s", e)
        
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
    Get the default global SparqlQueryExecutor instance with connection pooling.
    
    This provides a singleton executor for use across the application.
    Useful for simple cases where custom configuration isn't needed.
    Uses configuration values from config.py.
    
    Returns:
        The default SparqlQueryExecutor instance
        
    Example:
        from sparql_executor import get_default_executor
        
        executor = get_default_executor()
        results = executor.execute_query(query)
    """
    global _default_executor
    if _default_executor is None:
        from config import (
            SPARQL_TIMEOUT, SPARQL_MAX_RETRIES, SPARQL_RETRY_DELAY,
            SPARQL_CONNECTION_POOL_SIZE, SPARQL_USE_CONNECTION_POOL
        )
        _default_executor = SparqlQueryExecutor(
            timeout=SPARQL_TIMEOUT,
            max_retries=SPARQL_MAX_RETRIES,
            retry_delay=SPARQL_RETRY_DELAY,
            pool_size=SPARQL_CONNECTION_POOL_SIZE,
            use_connection_pool=SPARQL_USE_CONNECTION_POOL
        )
        logger.info(
            "Initialized default SPARQL executor",
            extra={
                'connection_pooling': SPARQL_USE_CONNECTION_POOL,
                'pool_size': SPARQL_CONNECTION_POOL_SIZE if SPARQL_USE_CONNECTION_POOL else 0
            }
        )
    return _default_executor
