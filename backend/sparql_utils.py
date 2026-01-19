"""
SPARQL Utility Functions Module

This module provides utility functions for working with SPARQL query results,
particularly for safely extracting values from result bindings with proper
error handling.

These utilities help prevent common errors when accessing SPARQL results and
provide consistent handling of missing or malformed data.
"""

from typing import Any, List, Dict, Optional


def safe_get_binding_value(
    bindings: List[Dict[str, Any]], 
    index: int, 
    key: str, 
    value_key: str = "value", 
    default: Any = None
) -> Any:
    """
    Safely extract a value from SPARQL query bindings with proper error handling.
    
    This function provides robust extraction of values from SPARQL result bindings,
    handling common edge cases like missing keys, out-of-bounds indices, and None values.
    
    Args:
        bindings (List[Dict[str, Any]]): The bindings list from SPARQL results
            Example: results["results"]["bindings"]
        index (int): The index to access in the bindings list
        key (str): The key in the binding to extract
            Example: "violationCount", "nodeShape", etc.
        value_key (str): The key for the value within the binding
            Usually "value" for literal values, could be "type" for type info
            Default: "value"
        default (Any): Default value to return if extraction fails
            Default: None
        
    Returns:
        Any: The extracted value from the binding, or the default value if:
            - The bindings list is empty or None
            - The index is out of bounds
            - The key doesn't exist in the binding
            - Any exception occurs during extraction
            
    Examples:
        >>> bindings = [{"count": {"value": "42", "type": "literal"}}]
        >>> safe_get_binding_value(bindings, 0, "count")
        '42'
        >>> safe_get_binding_value(bindings, 0, "missing", default="N/A")
        'N/A'
        >>> safe_get_binding_value([], 0, "count", default=0)
        0
    """
    try:
        if not bindings or index >= len(bindings):
            return default
        
        binding = bindings[index]
        if key not in binding:
            return default
        
        return binding[key].get(value_key, default)
    except (KeyError, IndexError, TypeError, AttributeError):
        return default


def safe_get_binding_int(
    bindings: List[Dict[str, Any]], 
    index: int, 
    key: str, 
    default: int = 0
) -> int:
    """
    Safely extract an integer value from SPARQL query bindings.
    
    This is a convenience wrapper around safe_get_binding_value that automatically
    converts the extracted value to an integer with proper error handling.
    
    Args:
        bindings (List[Dict[str, Any]]): The bindings list from SPARQL results
        index (int): The index to access in the bindings list
        key (str): The key in the binding to extract
        default (int): Default integer value if extraction or conversion fails
            Default: 0
        
    Returns:
        int: The extracted integer value, or the default value if:
            - Value extraction fails (see safe_get_binding_value)
            - Value cannot be converted to an integer
            
    Examples:
        >>> bindings = [{"count": {"value": "42"}}]
        >>> safe_get_binding_int(bindings, 0, "count")
        42
        >>> safe_get_binding_int(bindings, 0, "missing", default=10)
        10
        >>> bindings = [{"count": {"value": "invalid"}}]
        >>> safe_get_binding_int(bindings, 0, "count", default=0)
        0
    """
    value = safe_get_binding_value(bindings, index, key, default=str(default))
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_get_binding_float(
    bindings: List[Dict[str, Any]], 
    index: int, 
    key: str, 
    default: float = 0.0
) -> float:
    """
    Safely extract a float value from SPARQL query bindings.
    
    Similar to safe_get_binding_int but for floating-point numbers.
    
    Args:
        bindings (List[Dict[str, Any]]): The bindings list from SPARQL results
        index (int): The index to access in the bindings list
        key (str): The key in the binding to extract
        default (float): Default float value if extraction or conversion fails
            Default: 0.0
        
    Returns:
        float: The extracted float value, or the default value if:
            - Value extraction fails (see safe_get_binding_value)
            - Value cannot be converted to a float
            
    Examples:
        >>> bindings = [{"average": {"value": "3.14"}}]
        >>> safe_get_binding_float(bindings, 0, "average")
        3.14
        >>> safe_get_binding_float(bindings, 0, "missing", default=1.5)
        1.5
    """
    value = safe_get_binding_value(bindings, index, key, default=str(default))
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_get_all_binding_values(
    bindings: List[Dict[str, Any]], 
    key: str, 
    value_key: str = "value"
) -> List[Any]:
    """
    Safely extract all values for a given key from all bindings in a result set.
    
    This function iterates through all bindings and extracts the specified key,
    skipping any bindings where the key is missing or extraction fails.
    
    Args:
        bindings (List[Dict[str, Any]]): The bindings list from SPARQL results
        key (str): The key in the binding to extract from each result
        value_key (str): The key for the value within the binding
            Default: "value"
        
    Returns:
        List[Any]: A list of extracted values (empty list if no valid values found)
        
    Examples:
        >>> bindings = [
        ...     {"name": {"value": "Alice"}},
        ...     {"name": {"value": "Bob"}},
        ...     {"other": {"value": "Skip"}}
        ... ]
        >>> safe_get_all_binding_values(bindings, "name")
        ['Alice', 'Bob']
    """
    results = []
    for i in range(len(bindings)):
        value = safe_get_binding_value(bindings, i, key, value_key, default=None)
        if value is not None:
            results.append(value)
    return results
