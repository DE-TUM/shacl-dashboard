"""
Error Handling Utilities Module

This module provides decorators and utilities for consistent error handling
across API routes in the SHACL Dashboard application.

For standardized error codes and messages, see error_codes.py
"""

import logging
from functools import wraps
from flask import jsonify
from config import HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_INTERNAL_SERVER_ERROR, HTTP_FORBIDDEN
from error_codes import ErrorCodes, format_error_response, get_http_status_for_error_code

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """
    Raised when input validation fails.
    
    Attributes:
        message: Human-readable error message
        error_code: Optional error code from ErrorCodes
        details: Optional additional details dictionary
    """
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or ErrorCodes.VAL_INVALID_PARAMETER
        self.details = details or {}


class ResourceNotFoundError(Exception):
    """
    Raised when a requested resource is not found.
    
    Attributes:
        message: Human-readable error message
        error_code: Optional error code from ErrorCodes
        resource_type: Type of resource (e.g., 'graph', 'shape')
    """
    def __init__(self, message: str, error_code: str = None, resource_type: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or ErrorCodes.RES_GRAPH_NOT_FOUND
        self.resource_type = resource_type


class QueryExecutionError(Exception):
    """
    Raised when a SPARQL query execution fails.
    
    Attributes:
        message: Human-readable error message
        error_code: Optional error code from ErrorCodes
        query_info: Optional query details
    """
    def __init__(self, message: str, error_code: str = None, query_info: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or ErrorCodes.QRY_EXECUTION_FAILED
        self.query_info = query_info


def handle_api_errors(f):
    """
    Decorator to handle errors consistently across API routes with standardized error codes.
    
    Catches specific exceptions and returns appropriate HTTP responses with error codes:
    - ValidationError: 400 Bad Request (with error code)
    - ResourceNotFoundError: 404 Not Found (with error code)
    - QueryExecutionError: 500 Internal Server Error (with error code)
    - ValueError, KeyError, TypeError: 400 Bad Request (generic)
    - Other exceptions: 500 Internal Server Error (generic, no stack trace exposed)
    
    Usage:
        @app.route('/api/endpoint')
        @handle_api_errors
        def my_endpoint():
            # Your code here
            pass
    
    Returns:
        JSON response with structure:
        {
            "error_code": "ERROR_CODE",
            "message": "User-friendly error message"
        }
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(
                "Validation error in %s: %s (code: %s)", 
                f.__name__, e.message, e.error_code,
                extra={'error_code': e.error_code, 'details': e.details}
            )
            error_response = format_error_response(e.error_code, e.details)
            return jsonify(error_response), get_http_status_for_error_code(e.error_code)
            
        except ResourceNotFoundError as e:
            logger.warning(
                "Resource not found in %s: %s (code: %s)", 
                f.__name__, e.message, e.error_code,
                extra={'error_code': e.error_code, 'resource_type': e.resource_type}
            )
            error_response = format_error_response(e.error_code, {'resource': e.message})
            return jsonify(error_response), get_http_status_for_error_code(e.error_code)
            
        except QueryExecutionError as e:
            logger.error(
                "Query execution error in %s: %s (code: %s)", 
                f.__name__, e.message, e.error_code,
                extra={'error_code': e.error_code, 'query_info': e.query_info}
            )
            error_response = format_error_response(e.error_code)
            return jsonify(error_response), get_http_status_for_error_code(e.error_code)
            
        except (ValueError, KeyError, TypeError) as e:
            logger.warning("Invalid input in %s: %s", f.__name__, str(e))
            error_response = format_error_response(
                ErrorCodes.VAL_INVALID_PARAMETER,
                {'param': 'input', 'details': str(e)}
            )
            return jsonify(error_response), HTTP_BAD_REQUEST
            
        except Exception as e:
            # Never expose internal details to the client
            logger.exception("Unexpected error in %s", f.__name__)
            error_response = format_error_response(ErrorCodes.SYS_INTERNAL_ERROR)
            return jsonify(error_response), HTTP_INTERNAL_SERVER_ERROR
    
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
        raise ValidationError(
            f"{param_name} must be a non-empty string",
            error_code=ErrorCodes.VAL_INVALID_URI,
            details={'param': param_name, 'details': 'URI must be a non-empty string'}
        )
    
    uri = uri.strip()
    
    if not uri:
        raise ValidationError(
            f"{param_name} cannot be empty",
            error_code=ErrorCodes.VAL_INVALID_URI,
            details={'param': param_name, 'details': 'URI cannot be empty or whitespace'}
        )
    
    # Basic URI validation - should start with http:// or https://
    if not (uri.startswith('http://') or uri.startswith('https://')):
        raise ValidationError(
            f"{param_name} must be a valid HTTP(S) URI",
            error_code=ErrorCodes.VAL_INVALID_URI,
            details={'param': param_name, 'details': 'URI must start with http:// or https://'}
        )
    
    # Check for dangerous characters that could be used for SPARQL injection
    dangerous_chars = ['<', '>', '"', '{', '}', '|', '\\', '^', '`', '\n', '\r', '\t']
    for char in dangerous_chars:
        if char in uri:
            raise ValidationError(
                f"{param_name} contains invalid character: {repr(char)}",
                error_code=ErrorCodes.SEC_INJECTION_DETECTED,
                details={'param': param_name, 'details': f'Contains dangerous character: {repr(char)}'}
            )
    
    # Check for SPARQL keywords that could indicate injection attempts
    sparql_keywords = [
        'SELECT', 'INSERT', 'DELETE', 'DROP', 'CLEAR', 'LOAD', 'CREATE',
        'ASK', 'CONSTRUCT', 'DESCRIBE', 'GRAPH', 'WHERE', 'FILTER'
    ]
    uri_upper = uri.upper()
    for keyword in sparql_keywords:
        if f' {keyword} ' in uri_upper or uri_upper.endswith(f' {keyword}'):
            raise ValidationError(
                f"{param_name} contains suspicious SPARQL keyword: {keyword}",
                error_code=ErrorCodes.SEC_INJECTION_DETECTED,
                details={'param': param_name, 'details': f'Contains SPARQL keyword: {keyword}'}
            )
    
    # Check for comment patterns that could be used to bypass validation
    if '--' in uri or '#' in uri or '/*' in uri:
        raise ValidationError(
            f"{param_name} contains suspicious comment pattern",
            error_code=ErrorCodes.SEC_INJECTION_DETECTED,
            details={'param': param_name, 'details': 'Contains comment pattern'}
        )
    
    # Limit URI length to prevent DoS attacks
    if len(uri) > 2048:
        raise ValidationError(
            f"{param_name} exceeds maximum length of 2048 characters",
            error_code=ErrorCodes.VAL_OUT_OF_RANGE,
            details={'param': param_name, 'range': '1-2048 characters'}
        )
    
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
        raise ValidationError(
            f"{param_name} is required",
            error_code=ErrorCodes.VAL_MISSING_PARAMETER,
            details={'param': param_name}
        )
    
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(
            f"{param_name} must be a valid integer",
            error_code=ErrorCodes.VAL_INVALID_PARAMETER,
            details={'param': param_name, 'details': 'Must be a valid integer'}
        )
    
    if int_value < 0:
        raise ValidationError(
            f"{param_name} must be a positive integer",
            error_code=ErrorCodes.VAL_OUT_OF_RANGE,
            details={'param': param_name, 'range': '0 or greater'}
        )
    
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
