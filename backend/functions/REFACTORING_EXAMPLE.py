"""
Example: Refactored Validation Statistics Service

This is an EXAMPLE showing how to refactor validation_statistics_service.py 
to use the new SparqlQueryExecutor abstraction. This demonstrates the pattern
that should be applied to all service modules.

Key improvements in this refactored version:
1. Uses SparqlQueryExecutor instead of direct SPARQLWrapper calls
2. Eliminates boilerplate (setQuery, setReturnFormat, convert)
3. Automatic timeout and retry handling
4. Simplified error handling
5. Integrated logging through the executor
6. Easier to test (can mock the executor)
"""

import sys
import os
from typing import List, Dict, Optional, Any
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SHAPES_GRAPH_URI, VALIDATION_REPORT_URI
from sparql_executor import SparqlQueryExecutor, get_default_executor

logger = logging.getLogger(__name__)


def get_number_of_violations_in_validation_report(
    graph_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> int:
    """
    Query the SPARQL endpoint to get the total number of violations
    in the specified validation report graph.
    
    REFACTORED to use SparqlQueryExecutor for:
    - Automatic timeout handling
    - Retry logic with exponential backoff
    - Integrated logging
    - Simplified error handling

    Args:
        graph_uri: The target validation report graph URI to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided)

    Returns:
        The number of violations (sh:ValidationResult instances).
        
    Raises:
        SparqlQueryError: If the query fails after all retries
    """
    # Use provided executor or get the default singleton
    if executor is None:
        executor = get_default_executor()
    
    logger.info(
        "Getting violation count from validation report",
        extra={'function': 'get_number_of_violations_in_validation_report'}
    )
    
    # Build the SPARQL query
    query = f"""
    SELECT (COUNT(?violation) AS ?violationCount)
    FROM <{graph_uri}>
    WHERE {{
        ?report a <http://www.w3.org/ns/shacl#ValidationReport> ;
                <http://www.w3.org/ns/shacl#result> ?violation .
        ?violation a <http://www.w3.org/ns/shacl#ValidationResult> .
    }}
    """
    
    # Execute using the convenience method for count queries
    # The executor handles all the boilerplate, logging, retries, etc.
    violation_count = executor.execute_count_query(
        query,
        graph_uri=graph_uri,
        operation_name="get_violation_count",
        count_var="violationCount"
    )
    
    logger.info(
        "Successfully retrieved violation count",
        extra={'violation_count': violation_count}
    )
    
    return violation_count


def get_number_of_node_shapes(
    graph_uri: str = SHAPES_GRAPH_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> int:
    """
    Query the SPARQL endpoint to get the number of Node Shapes
    in the specified shapes graph.
    
    REFACTORED to use SparqlQueryExecutor.

    Args:
        graph_uri: The target shapes graph URI to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided)

    Returns:
        The number of Node Shapes in the shapes graph.
        
    Raises:
        SparqlQueryError: If the query fails after all retries
    """
    if executor is None:
        executor = get_default_executor()
    
    logger.info(
        "Getting node shapes count",
        extra={'function': 'get_number_of_node_shapes'}
    )
    
    query = f"""
    SELECT (COUNT(DISTINCT ?shape) AS ?shapeCount)
    FROM <{graph_uri}>
    WHERE {{
        ?shape a <http://www.w3.org/ns/shacl#NodeShape> .
    }}
    """
    
    shape_count = executor.execute_count_query(
        query,
        graph_uri=graph_uri,
        operation_name="get_node_shapes_count",
        count_var="shapeCount"
    )
    
    logger.info(
        "Successfully retrieved node shapes count",
        extra={'shape_count': shape_count}
    )
    
    return shape_count


def get_all_shapes_names(
    graph_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> List[str]:
    """
    Query the SPARQL endpoint to get all sh:sourceShape values
    from the specified graph.
    
    REFACTORED to use SparqlQueryExecutor.

    Args:
        graph_uri: The target graph URI to query.
        executor: Optional SparqlQueryExecutor instance (uses default if not provided)

    Returns:
        A list of shape name URIs.
        
    Raises:
        SparqlQueryError: If the query fails after all retries
    """
    if executor is None:
        executor = get_default_executor()
    
    logger.info(
        "Retrieving all shape names",
        extra={'function': 'get_all_shapes_names'}
    )
    
    query = f"""
    SELECT DISTINCT ?shape
    FROM <{graph_uri}>
    WHERE {{
        ?violation <http://www.w3.org/ns/shacl#sourceShape> ?shape .
    }}
    """
    
    # For non-count queries, use execute_query and extract results
    results = executor.execute_query(
        query,
        graph_uri=graph_uri,
        operation_name="get_shape_names"
    )
    
    # Extract shape URIs from results
    shapes = [
        result["shape"]["value"]
        for result in results["results"]["bindings"]
        if "shape" in result
    ]
    
    logger.info(
        "Successfully retrieved shape names",
        extra={'shape_count': len(shapes)}
    )
    
    return shapes


# COMPARISON: Before vs After

"""
BEFORE (Old Pattern - 20+ lines):
----------------------------------------
def get_number_of_violations_in_validation_report(graph_uri: str = VALIDATION_REPORT_URI) -> int:
    logger.info("Getting violation count from validation report")
    
    sparql = SPARQLWrapper(ENDPOINT_URL)  # Boilerplate
    query = "SELECT (COUNT(?violation) AS ?violationCount) ..."
    
    sparql.setQuery(query)                # Boilerplate
    sparql.setReturnFormat(JSON)          # Boilerplate

    try:
        start_time = time.time()          # Manual timing
        results = sparql.query().convert() # Boilerplate
        execution_time = time.time() - start_time
        
        log_sparql_query(logger, query, graph_uri, execution_time)  # Manual logging
        
        violation_count = int(results["results"]["bindings"][0]["violationCount"]["value"])
        
        logger.info("Successfully retrieved violation count")
        return violation_count

    except Exception as e:                # Generic error handling
        logger.error(f"Error querying validation report: {str(e)}")
        raise RuntimeError(f"Error querying validation report: {str(e)}")


AFTER (New Pattern - 10 lines):
----------------------------------------
def get_number_of_violations_in_validation_report(
    graph_uri: str = VALIDATION_REPORT_URI,
    executor: Optional[SparqlQueryExecutor] = None
) -> int:
    if executor is None:
        executor = get_default_executor()
    
    logger.info("Getting violation count from validation report")
    
    query = "SELECT (COUNT(?violation) AS ?violationCount) ..."
    
    # All boilerplate, timing, logging, retries handled by executor!
    return executor.execute_count_query(
        query,
        graph_uri=graph_uri,
        operation_name="get_violation_count",
        count_var="violationCount"
    )


BENEFITS:
1. 50% less code
2. Automatic timeout handling (no hanging queries)
3. Automatic retry with exponential backoff (more reliable)
4. Integrated logging (no manual time tracking)
5. Easier to test (can inject mock executor)
6. Consistent error handling across all services
7. Single place to add caching, metrics, etc. in the future
"""
