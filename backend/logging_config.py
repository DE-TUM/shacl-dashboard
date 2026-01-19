"""
Logging Configuration Module

This module provides comprehensive structured logging for the SHACL Dashboard backend.
It includes:
- JSON formatted logging for production environments
- Request correlation IDs for tracing
- SPARQL query logging
- Sanitization of sensitive information
- Configurable log levels per module

Usage:
    from logging_config import get_logger, log_sparql_query, setup_request_logging
    
    logger = get_logger(__name__)
    logger.info("Processing request", extra={"user_id": 123})
"""

import logging
import json
import sys
from typing import Any, Dict, Optional
from datetime import datetime
import contextvars
from functools import wraps
import time

# Context variable for request correlation ID
correlation_id_var = contextvars.ContextVar('correlation_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Outputs log records as JSON with additional context fields like
    correlation_id, timestamp, and custom fields passed via extra.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add correlation ID if present
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data['correlation_id'] = correlation_id
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add any extra fields passed via extra parameter
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'lineno', 'module', 'msecs', 'message',
                          'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data)


class SanitizingFilter(logging.Filter):
    """
    Logging filter that sanitizes sensitive information from log messages.
    
    Prevents logging of:
    - Passwords and credentials
    - API keys and tokens
    - Full URIs that might contain sensitive data (only logs domain)
    """
    
    SENSITIVE_PATTERNS = [
        'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'credential',
        'authorization', 'auth', 'api_key', 'apikey'
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize sensitive information from log record."""
        message = record.getMessage().lower()
        
        # Check if message contains sensitive patterns
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message:
                record.msg = self._sanitize_message(str(record.msg))
                record.args = ()
        
        return True
    
    def _sanitize_message(self, message: str) -> str:
        """Replace sensitive information with asterisks."""
        return "[REDACTED - Contains sensitive information]"


def setup_logging(log_level: str = "INFO", use_json: bool = False) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: If True, use JSON formatter; otherwise use standard format
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))
    
    # Set formatter
    if use_json:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    
    # Add sanitizing filter
    handler.addFilter(SanitizingFilter())
    
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID for the current request context.
    
    Args:
        correlation_id: Unique identifier for request tracing
    """
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """
    Get the correlation ID for the current request context.
    
    Returns:
        Correlation ID or None if not set
    """
    return correlation_id_var.get()


def log_sparql_query(logger: logging.Logger, query: str, graph_uri: str = None,
                     execution_time: float = None) -> None:
    """
    Log SPARQL query execution with sanitized details.
    
    Args:
        logger: Logger instance to use
        query: SPARQL query string (will be truncated for logging)
        graph_uri: Graph URI being queried (domain only for security)
        execution_time: Query execution time in seconds
    """
    # Truncate query for logging
    query_preview = query[:200] + "..." if len(query) > 200 else query
    query_preview = query_preview.replace('\n', ' ').strip()
    
    # Sanitize graph URI - only log domain/host
    sanitized_uri = _sanitize_uri(graph_uri) if graph_uri else None
    
    log_data = {
        'event': 'sparql_query',
        'query_preview': query_preview,
        'query_length': len(query),
    }
    
    if sanitized_uri:
        log_data['graph_domain'] = sanitized_uri
    
    if execution_time is not None:
        log_data['execution_time_seconds'] = round(execution_time, 3)
    
    logger.info("SPARQL query executed", extra=log_data)


def _sanitize_uri(uri: str) -> str:
    """Extract and return only the domain from a URI for logging."""
    if not uri:
        return ""
    
    # Extract domain/protocol only
    if "://" in uri:
        parts = uri.split("://")
        if len(parts) > 1:
            domain_part = parts[1].split("/")[0]
            return f"{parts[0]}://{domain_part}"
    
    return "[URI]"


def log_function_call(logger: logging.Logger = None):
    """
    Decorator to log function entry and exit with execution time.
    
    Usage:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            return result
    
    Args:
        logger: Logger instance (if None, creates one from function's module)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger if not provided
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            # Log function entry
            func_name = func.__qualname__
            logger.debug(
                f"Entering {func_name}",
                extra={
                    'event': 'function_entry',
                    'function': func_name,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
            )
            
            # Execute function and measure time
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log function exit
                logger.debug(
                    f"Exiting {func_name}",
                    extra={
                        'event': 'function_exit',
                        'function': func_name,
                        'execution_time_seconds': round(execution_time, 3),
                        'success': True
                    }
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Log function error
                logger.error(
                    f"Error in {func_name}: {str(e)}",
                    extra={
                        'event': 'function_error',
                        'function': func_name,
                        'execution_time_seconds': round(execution_time, 3),
                        'error_type': type(e).__name__,
                        'success': False
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_api_request(logger: logging.Logger, method: str, path: str,
                    params: Dict[str, Any] = None) -> None:
    """
    Log API request details.
    
    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, etc.)
        path: Request path
        params: Request parameters (will be sanitized)
    """
    log_data = {
        'event': 'api_request',
        'method': method,
        'path': path,
    }
    
    if params:
        # Sanitize parameters (don't log full URIs)
        sanitized_params = {}
        for key, value in params.items():
            if 'uri' in key.lower() and value:
                sanitized_params[key] = _sanitize_uri(str(value))
            else:
                sanitized_params[key] = value
        log_data['params'] = sanitized_params
    
    logger.info("API request received", extra=log_data)


def log_api_response(logger: logging.Logger, status_code: int,
                     execution_time: float = None) -> None:
    """
    Log API response details.
    
    Args:
        logger: Logger instance
        status_code: HTTP status code
        execution_time: Request execution time in seconds
    """
    log_data = {
        'event': 'api_response',
        'status_code': status_code,
    }
    
    if execution_time is not None:
        log_data['execution_time_seconds'] = round(execution_time, 3)
    
    level = logging.INFO if status_code < 400 else logging.ERROR
    logger.log(level, f"API response: {status_code}", extra=log_data)
