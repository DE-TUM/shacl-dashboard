"""
Service Layer Validators Module

This module provides validation functions and Pydantic models for validating
inputs at the service layer, not just at the route layer. This ensures that
service functions can be safely called from any context and fail fast with
clear error messages.

Key Features:
- Pydantic models for structured data validation
- Custom validation functions for URIs, integers, limits/offsets
- Type-safe validation with clear error messages
- Reusable across all service modules

Usage:
    from validators import validate_graph_uri, validate_limit_offset, GraphUriModel
    
    # Validate a single URI
    validated_uri = validate_graph_uri(user_input)
    
    # Validate structured data
    model = GraphUriModel(graph_uri=user_input)
    validated_uri = model.graph_uri
"""

from pydantic import BaseModel, Field, validator, ValidationError as PydanticValidationError
from typing import Optional
import re


class ValidationError(Exception):
    """Custom exception for validation errors at service layer."""
    pass


class GraphUriModel(BaseModel):
    """Pydantic model for validating graph URIs."""
    
    graph_uri: str = Field(..., min_length=1, max_length=2048, description="Graph URI to validate")
    
    @validator('graph_uri')
    def validate_uri_format(cls, v):
        """Validate that the graph URI is properly formatted and safe."""
        if not v or not v.strip():
            raise ValueError("Graph URI cannot be empty")
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', '"', '{', '}', '|', '\\', '^', '`', '\n', '\r', '\t']
        if any(char in v for char in dangerous_chars):
            raise ValueError(f"Graph URI contains dangerous characters")
        
        # Check for SPARQL injection patterns
        sparql_keywords = [
            'SELECT', 'INSERT', 'DELETE', 'DROP', 'CREATE', 'LOAD', 'CLEAR',
            'CONSTRUCT', 'DESCRIBE', 'ASK', 'UNION', 'OPTIONAL', 'FILTER'
        ]
        upper_v = v.upper()
        if any(keyword in upper_v for keyword in sparql_keywords):
            raise ValueError(f"Graph URI contains suspicious SPARQL keywords")
        
        # Check for comment patterns
        if '--' in v or '#' in v or '/*' in v:
            raise ValueError(f"Graph URI contains comment patterns")
        
        # Must be a valid URI format (http:// or https://)
        uri_pattern = r'^https?://[^\s]+$'
        if not re.match(uri_pattern, v):
            raise ValueError(f"Graph URI must be a valid HTTP(S) URI")
        
        return v


class LimitOffsetModel(BaseModel):
    """Pydantic model for validating pagination parameters."""
    
    limit: Optional[int] = Field(None, ge=1, le=10000, description="Maximum number of results to return")
    offset: Optional[int] = Field(None, ge=0, description="Number of results to skip")
    
    @validator('limit')
    def validate_limit(cls, v):
        """Ensure limit is reasonable."""
        if v is not None and v > 10000:
            raise ValueError("Limit cannot exceed 10000")
        return v


class NodeShapeNameModel(BaseModel):
    """Pydantic model for validating node shape names."""
    
    node_shape: str = Field(..., min_length=1, max_length=2048, description="Node shape URI")
    
    @validator('node_shape')
    def validate_node_shape_uri(cls, v):
        """Validate that the node shape URI is properly formatted."""
        if not v or not v.strip():
            raise ValueError("Node shape URI cannot be empty")
        
        # Check length
        if len(v) > 2048:
            raise ValueError("Node shape URI too long (max 2048 characters)")
        
        # Must be a valid URI format
        uri_pattern = r'^https?://[^\s]+$'
        if not re.match(uri_pattern, v):
            raise ValueError("Node shape must be a valid HTTP(S) URI")
        
        return v


def validate_graph_uri(uri: str, param_name: str = "graph_uri") -> str:
    """
    Validate a graph URI at the service layer.
    
    This function provides consistent validation for graph URIs across all service functions.
    It checks for:
    - Non-empty value
    - Dangerous characters
    - SPARQL injection patterns
    - Valid URI format
    - Reasonable length
    
    Args:
        uri: The URI string to validate
        param_name: Name of the parameter (for error messages)
    
    Returns:
        str: The validated URI
    
    Raises:
        ValidationError: If the URI is invalid
    
    Example:
        >>> validated_uri = validate_graph_uri("http://ex.org/Graph")
        >>> print(validated_uri)
        'http://ex.org/Graph'
    """
    try:
        model = GraphUriModel(graph_uri=uri)
        return model.graph_uri
    except PydanticValidationError as e:
        errors = e.errors()
        error_messages = [err['msg'] for err in errors]
        raise ValidationError(f"Invalid {param_name}: {'; '.join(error_messages)}")


def validate_limit_offset(limit: Optional[int] = None, offset: Optional[int] = None) -> tuple:
    """
    Validate pagination parameters at the service layer.
    
    Args:
        limit: Maximum number of results (1-10000)
        offset: Number of results to skip (>= 0)
    
    Returns:
        tuple: (validated_limit, validated_offset)
    
    Raises:
        ValidationError: If parameters are invalid
    
    Example:
        >>> limit, offset = validate_limit_offset(10, 0)
        >>> print(f"Limit: {limit}, Offset: {offset}")
        Limit: 10, Offset: 0
    """
    try:
        model = LimitOffsetModel(limit=limit, offset=offset)
        return model.limit, model.offset
    except PydanticValidationError as e:
        errors = e.errors()
        error_messages = [err['msg'] for err in errors]
        raise ValidationError(f"Invalid pagination parameters: {'; '.join(error_messages)}")


def validate_node_shape_uri(uri: str, param_name: str = "node_shape") -> str:
    """
    Validate a node shape URI at the service layer.
    
    Args:
        uri: The node shape URI to validate
        param_name: Name of the parameter (for error messages)
    
    Returns:
        str: The validated URI
    
    Raises:
        ValidationError: If the URI is invalid
    
    Example:
        >>> validated_uri = validate_node_shape_uri("http://ex.org/PersonShape")
        >>> print(validated_uri)
        'http://ex.org/PersonShape'
    """
    try:
        model = NodeShapeNameModel(node_shape=uri)
        return model.node_shape
    except PydanticValidationError as e:
        errors = e.errors()
        error_messages = [err['msg'] for err in errors]
        raise ValidationError(f"Invalid {param_name}: {'; '.join(error_messages)}")


def validate_positive_int(value: int, param_name: str = "value", min_value: int = 1, max_value: Optional[int] = None) -> int:
    """
    Validate a positive integer at the service layer.
    
    Args:
        value: The integer to validate
        param_name: Name of the parameter (for error messages)
        min_value: Minimum allowed value (default: 1)
        max_value: Maximum allowed value (default: None)
    
    Returns:
        int: The validated integer
    
    Raises:
        ValidationError: If the value is invalid
    
    Example:
        >>> validated_count = validate_positive_int(10, "count", min_value=1, max_value=100)
        >>> print(validated_count)
        10
    """
    if not isinstance(value, int):
        raise ValidationError(f"{param_name} must be an integer")
    
    if value < min_value:
        raise ValidationError(f"{param_name} must be at least {min_value}")
    
    if max_value is not None and value > max_value:
        raise ValidationError(f"{param_name} must not exceed {max_value}")
    
    return value


def validate_non_empty_string(value: str, param_name: str = "value", max_length: int = 2048) -> str:
    """
    Validate a non-empty string at the service layer.
    
    Args:
        value: The string to validate
        param_name: Name of the parameter (for error messages)
        max_length: Maximum allowed length (default: 2048)
    
    Returns:
        str: The validated string
    
    Raises:
        ValidationError: If the string is invalid
    
    Example:
        >>> validated_name = validate_non_empty_string("PersonShape", "shape_name")
        >>> print(validated_name)
        'PersonShape'
    """
    if not isinstance(value, str):
        raise ValidationError(f"{param_name} must be a string")
    
    if not value or not value.strip():
        raise ValidationError(f"{param_name} cannot be empty")
    
    if len(value) > max_length:
        raise ValidationError(f"{param_name} too long (max {max_length} characters)")
    
    return value.strip()
