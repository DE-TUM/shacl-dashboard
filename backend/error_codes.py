"""
Error Codes Module

This module defines standardized error codes and user-friendly error messages
for the SHACL Dashboard API. Error codes follow the pattern: CATEGORY_SPECIFIC_ERROR

Categories:
- VAL_* : Validation errors (400)
- RES_* : Resource not found errors (404)
- QRY_* : Query execution errors (500)
- SYS_* : System/internal errors (500)
- SEC_* : Security-related errors (403)
"""

from typing import Dict, Tuple

# Error code constants
class ErrorCodes:
    """Standardized error codes for the API."""
    
    # Validation Errors (400)
    VAL_INVALID_URI = "VAL_INVALID_URI"
    VAL_INVALID_PARAMETER = "VAL_INVALID_PARAMETER"
    VAL_MISSING_PARAMETER = "VAL_MISSING_PARAMETER"
    VAL_INVALID_FORMAT = "VAL_INVALID_FORMAT"
    VAL_OUT_OF_RANGE = "VAL_OUT_OF_RANGE"
    
    # Resource Not Found Errors (404)
    RES_GRAPH_NOT_FOUND = "RES_GRAPH_NOT_FOUND"
    RES_SHAPE_NOT_FOUND = "RES_SHAPE_NOT_FOUND"
    RES_VIOLATION_NOT_FOUND = "RES_VIOLATION_NOT_FOUND"
    RES_REPORT_NOT_FOUND = "RES_REPORT_NOT_FOUND"
    
    # Query Execution Errors (500)
    QRY_EXECUTION_FAILED = "QRY_EXECUTION_FAILED"
    QRY_TIMEOUT = "QRY_TIMEOUT"
    QRY_INVALID_SYNTAX = "QRY_INVALID_SYNTAX"
    QRY_CONNECTION_ERROR = "QRY_CONNECTION_ERROR"
    
    # System Errors (500)
    SYS_INTERNAL_ERROR = "SYS_INTERNAL_ERROR"
    SYS_SERVICE_UNAVAILABLE = "SYS_SERVICE_UNAVAILABLE"
    SYS_CONFIGURATION_ERROR = "SYS_CONFIGURATION_ERROR"
    
    # Security Errors (403)
    SEC_INJECTION_DETECTED = "SEC_INJECTION_DETECTED"
    SEC_UNAUTHORIZED = "SEC_UNAUTHORIZED"
    SEC_FORBIDDEN = "SEC_FORBIDDEN"


# User-friendly error messages
ERROR_MESSAGES: Dict[str, str] = {
    # Validation Errors
    ErrorCodes.VAL_INVALID_URI: "The provided URI format is invalid. Please provide a valid HTTP(S) URI.",
    ErrorCodes.VAL_INVALID_PARAMETER: "The parameter '{param}' has an invalid value. {details}",
    ErrorCodes.VAL_MISSING_PARAMETER: "Required parameter '{param}' is missing.",
    ErrorCodes.VAL_INVALID_FORMAT: "The data format is invalid. Expected: {expected}",
    ErrorCodes.VAL_OUT_OF_RANGE: "The value for '{param}' is out of valid range. Valid range: {range}",
    
    # Resource Not Found Errors
    ErrorCodes.RES_GRAPH_NOT_FOUND: "The requested graph '{graph}' was not found in the triple store.",
    ErrorCodes.RES_SHAPE_NOT_FOUND: "The shape '{shape}' was not found.",
    ErrorCodes.RES_VIOLATION_NOT_FOUND: "No violations found for the specified criteria.",
    ErrorCodes.RES_REPORT_NOT_FOUND: "The validation report was not found. Please ensure data is loaded.",
    
    # Query Execution Errors
    ErrorCodes.QRY_EXECUTION_FAILED: "Failed to execute the query. Please try again later.",
    ErrorCodes.QRY_TIMEOUT: "The query took too long to execute and was terminated. Please refine your query.",
    ErrorCodes.QRY_INVALID_SYNTAX: "The query syntax is invalid.",
    ErrorCodes.QRY_CONNECTION_ERROR: "Unable to connect to the database. Please check the connection settings.",
    
    # System Errors
    ErrorCodes.SYS_INTERNAL_ERROR: "An internal error occurred. Our team has been notified.",
    ErrorCodes.SYS_SERVICE_UNAVAILABLE: "The service is temporarily unavailable. Please try again later.",
    ErrorCodes.SYS_CONFIGURATION_ERROR: "System configuration error. Please contact support.",
    
    # Security Errors
    ErrorCodes.SEC_INJECTION_DETECTED: "Potential security threat detected. Request has been blocked.",
    ErrorCodes.SEC_UNAUTHORIZED: "Authentication required to access this resource.",
    ErrorCodes.SEC_FORBIDDEN: "You do not have permission to access this resource.",
}


def format_error_response(error_code: str, details: Dict[str, str] = None) -> Dict[str, str]:
    """
    Format a standardized error response.
    
    Args:
        error_code: One of the ErrorCodes constants
        details: Optional dictionary with additional details to format into the message
        
    Returns:
        Dict with 'error_code', 'message', and optionally 'details'
        
    Example:
        >>> format_error_response(ErrorCodes.VAL_INVALID_PARAMETER, 
        ...                       {'param': 'limit', 'details': 'Must be positive'})
        {
            'error_code': 'VAL_INVALID_PARAMETER',
            'message': "The parameter 'limit' has an invalid value. Must be positive"
        }
    """
    message = ERROR_MESSAGES.get(error_code, ERROR_MESSAGES[ErrorCodes.SYS_INTERNAL_ERROR])
    
    if details:
        try:
            message = message.format(**details)
        except KeyError:
            # If formatting fails, return message as-is
            pass
    
    response = {
        'error_code': error_code,
        'message': message
    }
    
    return response


def get_http_status_for_error_code(error_code: str) -> int:
    """
    Get the appropriate HTTP status code for an error code.
    
    Args:
        error_code: One of the ErrorCodes constants
        
    Returns:
        HTTP status code (400, 403, 404, or 500)
    """
    if error_code.startswith('VAL_'):
        return 400  # Bad Request
    elif error_code.startswith('RES_'):
        return 404  # Not Found
    elif error_code.startswith('SEC_'):
        return 403  # Forbidden
    else:  # QRY_* or SYS_*
        return 500  # Internal Server Error
