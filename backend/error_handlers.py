"""
Error Handling Utilities Module

This module provides decorators and utilities for consistent error handling
across API routes in the SHACL Dashboard application.
"""

import logging
from functools import wraps
from flask import jsonify
from config import HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_INTERNAL_SERVER_ERROR

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class ResourceNotFoundError(Exception):
    """Raised when a requested resource is not found."""
    pass


def handle_api_errors(f):
    """
    Decorator to handle errors consistently across API routes.
    
    Catches specific exceptions and returns appropriate HTTP responses:
    - ValidationError: 400 Bad Request
    - ResourceNotFoundError: 404 Not Found
    - ValueError, KeyError, TypeError: 400 Bad Request
    - Other exceptions: 500 Internal Server Error
    
    Usage:
        @app.route('/api/endpoint')
        @handle_api_errors
        def my_endpoint():
            # Your code here
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning("Validation error in %s: %s", f.__name__, str(e))
            return jsonify({'error': str(e)}), HTTP_BAD_REQUEST
        except ResourceNotFoundError as e:
            logger.warning("Resource not found in %s: %s", f.__name__, str(e))
            return jsonify({'error': str(e)}), HTTP_NOT_FOUND
        except (ValueError, KeyError, TypeError) as e:
            logger.warning("Invalid input in %s: %s", f.__name__, str(e))
            return jsonify({'error': f'Invalid input: {str(e)}'}), HTTP_BAD_REQUEST
        except Exception as e:
            logger.exception("Unexpected error in %s", f.__name__)
            return jsonify({'error': 'Internal server error'}), HTTP_INTERNAL_SERVER_ERROR
    
    return decorated_function


def validate_uri(uri: str, param_name: str = "URI") -> str:
    """
    Validate that a string is a valid URI format and safe for use in SPARQL queries.
    
    This function performs comprehensive validation to prevent SPARQL injection attacks
    by checking for malicious characters and patterns that could compromise query integrity.
    
    Args:
        uri (str): The URI string to validate
        param_name (str): Name of the parameter for error messages
        
    Returns:
        str: The validated URI
        
    Raises:
        ValidationError: If the URI is invalid or contains potentially malicious content
    """
    if not uri or not isinstance(uri, str):
        raise ValidationError(f"{param_name} must be a non-empty string")
    
    uri = uri.strip()
    
    if not uri:
        raise ValidationError(f"{param_name} cannot be empty")
    
    # Basic URI validation - should start with http:// or https://
    if not (uri.startswith('http://') or uri.startswith('https://')):
        raise ValidationError(f"{param_name} must be a valid HTTP(S) URI")
    
    # Check for dangerous characters that could be used for SPARQL injection
    dangerous_chars = ['<', '>', '"', '{', '}', '|', '\\', '^', '`', '\n', '\r', '\t']
    for char in dangerous_chars:
        if char in uri:
            raise ValidationError(f"{param_name} contains invalid character: {repr(char)}")
    
    # Check for SPARQL keywords that could indicate injection attempts
    sparql_keywords = [
        'SELECT', 'INSERT', 'DELETE', 'DROP', 'CLEAR', 'LOAD', 'CREATE',
        'ASK', 'CONSTRUCT', 'DESCRIBE', 'GRAPH', 'WHERE', 'FILTER'
    ]
    uri_upper = uri.upper()
    for keyword in sparql_keywords:
        if f' {keyword} ' in uri_upper or uri_upper.endswith(f' {keyword}'):
            raise ValidationError(f"{param_name} contains suspicious SPARQL keyword: {keyword}")
    
    # Check for comment patterns that could be used to bypass validation
    if '--' in uri or '#' in uri or '/*' in uri:
        raise ValidationError(f"{param_name} contains suspicious comment pattern")
    
    # Limit URI length to prevent DoS attacks
    if len(uri) > 2048:
        raise ValidationError(f"{param_name} exceeds maximum length of 2048 characters")
    
    return uri


def validate_positive_integer(value: any, param_name: str = "value", allow_none: bool = True) -> int:
    """
    Validate and convert a value to a positive integer.
    
    Args:
        value: The value to validate
        param_name (str): Name of the parameter for error messages
        allow_none (bool): Whether None is allowed
        
    Returns:
        int: The validated integer, or None if allowed
        
    Raises:
        ValidationError: If the value is invalid
    """
    if value is None:
        if allow_none:
            return None
        raise ValidationError(f"{param_name} is required")
    
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{param_name} must be a valid integer")
    
    if int_value < 0:
        raise ValidationError(f"{param_name} must be a positive integer")
    
    return int_value


def safe_get_binding_value(bindings: list, index: int, key: str, value_key: str = "value", default=None):
    """
    DEPRECATED: This function has been moved to sparql_utils module.
    Kept here for backward compatibility. Please use sparql_utils.safe_get_binding_value instead.
    
    Safely extract a value from SPARQL query bindings with proper error handling.
    
    Args:
        bindings (list): The bindings list from SPARQL results
        index (int): The index to access
        key (str): The key in the binding
        value_key (str): The key for the value (usually "value")
        default: Default value if extraction fails
        
    Returns:
        The extracted value or default
    """
    from sparql_utils import safe_get_binding_value as _safe_get_binding_value
    return _safe_get_binding_value(bindings, index, key, value_key, default)


def safe_get_binding_int(bindings: list, index: int, key: str, default: int = 0) -> int:
    """
    DEPRECATED: This function has been moved to sparql_utils module.
    Kept here for backward compatibility. Please use sparql_utils.safe_get_binding_int instead.
    
    Safely extract an integer value from SPARQL query bindings.
    
    Args:
        bindings (list): The bindings list from SPARQL results
        index (int): The index to access
        key (str): The key in the binding
        default (int): Default value if extraction fails
        
    Returns:
        int: The extracted integer value or default
    """
    from sparql_utils import safe_get_binding_int as _safe_get_binding_int
    return _safe_get_binding_int(bindings, index, key, default)
