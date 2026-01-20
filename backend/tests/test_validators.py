"""
Unit Tests for validators.py

Tests for service-layer input validation functions and Pydantic models.
Tests cover valid inputs, invalid inputs, SPARQL injection attempts, and edge cases.
"""

import pytest
from validators import (
    validate_graph_uri,
    validate_limit_offset,
    validate_node_shape_uri,
    validate_positive_int,
    validate_non_empty_string,
    ValidationError,
    GraphUriModel,
    LimitOffsetModel,
    NodeShapeNameModel
)


class TestGraphUriValidation:
    """Tests for graph URI validation."""
    
    def test_valid_http_uri(self):
        """Test that valid HTTP URIs pass validation."""
        uri = validate_graph_uri("http://ex.org/ShapesGraph")
        assert uri == "http://ex.org/ShapesGraph"
    
    def test_valid_https_uri(self):
        """Test that valid HTTPS URIs pass validation."""
        uri = validate_graph_uri("https://example.com/graph")
        assert uri == "https://example.com/graph"
    
    def test_empty_uri_rejected(self):
        """Test that empty URIs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_graph_uri("")
        error_msg = str(exc_info.value).lower()
        assert "empty" in error_msg or "at least 1 character" in error_msg
    
    def test_whitespace_only_uri_rejected(self):
        """Test that whitespace-only URIs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_graph_uri("   ")
        assert "empty" in str(exc_info.value).lower()
    
    def test_dangerous_characters_rejected(self):
        """Test that URIs with dangerous characters are rejected."""
        dangerous_uris = [
            "http://ex.org/<script>",
            "http://ex.org/test\"value",
            "http://ex.org/{injection}",
            "http://ex.org/test|pipe",
            "http://ex.org/test\\backslash",
            "http://ex.org/test^caret",
            "http://ex.org/test`backtick"
        ]
        for uri in dangerous_uris:
            with pytest.raises(ValidationError) as exc_info:
                validate_graph_uri(uri)
            assert "dangerous characters" in str(exc_info.value).lower()
    
    def test_sparql_injection_keywords_rejected(self):
        """Test that URIs containing SPARQL keywords are rejected."""
        injection_attempts = [
            "http://ex.org/'; SELECT * WHERE",
            "http://ex.org/test'; DROP GRAPH",
            "http://ex.org/test'; INSERT DATA",
            "http://ex.org/test'; DELETE WHERE",
            "http://ex.org/UNION",
            "http://ex.org/OPTIONAL",
            "http://ex.org/FILTER"
        ]
        for uri in injection_attempts:
            with pytest.raises(ValidationError) as exc_info:
                validate_graph_uri(uri)
            assert "sparql" in str(exc_info.value).lower()
    
    def test_comment_patterns_rejected(self):
        """Test that URIs with comment patterns are rejected."""
        comment_uris = [
            "http://ex.org/test--comment",
            "http://ex.org/test#fragment",
            "http://ex.org/test/*comment*/"
        ]
        for uri in comment_uris:
            with pytest.raises(ValidationError) as exc_info:
                validate_graph_uri(uri)
            assert "comment" in str(exc_info.value).lower()
    
    def test_uri_too_long_rejected(self):
        """Test that URIs exceeding 2048 characters are rejected."""
        long_uri = "http://ex.org/" + "a" * 2050
        with pytest.raises(ValidationError) as exc_info:
            validate_graph_uri(long_uri)
        assert "2048" in str(exc_info.value) or "long" in str(exc_info.value).lower()
    
    def test_non_http_uri_rejected(self):
        """Test that non-HTTP(S) URIs are rejected."""
        invalid_uris = [
            "ftp://ex.org/graph",
            "file:///path/to/file",
            "urn:example:graph",
            "just-a-string"
        ]
        for uri in invalid_uris:
            with pytest.raises(ValidationError) as exc_info:
                validate_graph_uri(uri)
            assert "http" in str(exc_info.value).lower() or "uri" in str(exc_info.value).lower()
    
    def test_custom_param_name_in_error(self):
        """Test that custom parameter names appear in error messages."""
        with pytest.raises(ValidationError) as exc_info:
            validate_graph_uri("", "custom_param")
        assert "custom_param" in str(exc_info.value)


class TestLimitOffsetValidation:
    """Tests for pagination parameter validation."""
    
    def test_valid_limit_offset(self):
        """Test valid limit and offset values."""
        limit, offset = validate_limit_offset(10, 0)
        assert limit == 10
        assert offset == 0
    
    def test_none_values_accepted(self):
        """Test that None values are accepted."""
        limit, offset = validate_limit_offset(None, None)
        assert limit is None
        assert offset is None
    
    def test_limit_minimum_boundary(self):
        """Test limit minimum boundary (1)."""
        limit, offset = validate_limit_offset(1, 0)
        assert limit == 1
    
    def test_limit_maximum_boundary(self):
        """Test limit maximum boundary (10000)."""
        limit, offset = validate_limit_offset(10000, 0)
        assert limit == 10000
    
    def test_limit_below_minimum_rejected(self):
        """Test that limit below 1 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_limit_offset(0, 0)
        assert "greater than or equal to 1" in str(exc_info.value).lower() or "ensure this value is greater" in str(exc_info.value).lower()
    
    def test_limit_above_maximum_rejected(self):
        """Test that limit above 10000 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_limit_offset(10001, 0)
        assert "10000" in str(exc_info.value)
    
    def test_negative_offset_rejected(self):
        """Test that negative offset is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_limit_offset(10, -1)
        assert "greater than or equal to 0" in str(exc_info.value).lower() or "ensure this value is greater" in str(exc_info.value).lower()
    
    def test_offset_zero_accepted(self):
        """Test that offset of 0 is accepted."""
        limit, offset = validate_limit_offset(10, 0)
        assert offset == 0
    
    def test_large_offset_accepted(self):
        """Test that large offset values are accepted."""
        limit, offset = validate_limit_offset(10, 100000)
        assert offset == 100000


class TestNodeShapeUriValidation:
    """Tests for node shape URI validation."""
    
    def test_valid_node_shape_uri(self):
        """Test that valid node shape URIs pass validation."""
        uri = validate_node_shape_uri("http://ex.org/PersonShape")
        assert uri == "http://ex.org/PersonShape"
    
    def test_empty_node_shape_rejected(self):
        """Test that empty node shape URIs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_node_shape_uri("")
        error_msg = str(exc_info.value).lower()
        assert "empty" in error_msg or "at least 1 character" in error_msg
    
    def test_node_shape_too_long_rejected(self):
        """Test that node shape URIs exceeding 2048 characters are rejected."""
        long_uri = "http://ex.org/" + "a" * 2050
        with pytest.raises(ValidationError) as exc_info:
            validate_node_shape_uri(long_uri)
        assert "2048" in str(exc_info.value) or "long" in str(exc_info.value).lower()
    
    def test_non_http_node_shape_rejected(self):
        """Test that non-HTTP(S) node shape URIs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_node_shape_uri("not-a-uri")
        assert "http" in str(exc_info.value).lower() or "uri" in str(exc_info.value).lower()


class TestPositiveIntValidation:
    """Tests for positive integer validation."""
    
    def test_valid_positive_int(self):
        """Test that valid positive integers pass validation."""
        result = validate_positive_int(10, "count")
        assert result == 10
    
    def test_minimum_value_enforced(self):
        """Test that minimum value is enforced."""
        result = validate_positive_int(5, "count", min_value=5)
        assert result == 5
    
    def test_below_minimum_rejected(self):
        """Test that values below minimum are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_int(4, "count", min_value=5)
        assert "at least 5" in str(exc_info.value)
    
    def test_maximum_value_enforced(self):
        """Test that maximum value is enforced."""
        result = validate_positive_int(10, "count", max_value=10)
        assert result == 10
    
    def test_above_maximum_rejected(self):
        """Test that values above maximum are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_int(11, "count", max_value=10)
        assert "not exceed 10" in str(exc_info.value)
    
    def test_non_integer_rejected(self):
        """Test that non-integer values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_int("10", "count")
        assert "integer" in str(exc_info.value).lower()


class TestNonEmptyStringValidation:
    """Tests for non-empty string validation."""
    
    def test_valid_string(self):
        """Test that valid strings pass validation."""
        result = validate_non_empty_string("PersonShape", "shape_name")
        assert result == "PersonShape"
    
    def test_string_with_whitespace_trimmed(self):
        """Test that strings with leading/trailing whitespace are trimmed."""
        result = validate_non_empty_string("  PersonShape  ", "shape_name")
        assert result == "PersonShape"
    
    def test_empty_string_rejected(self):
        """Test that empty strings are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_non_empty_string("", "shape_name")
        assert "empty" in str(exc_info.value).lower()
    
    def test_whitespace_only_rejected(self):
        """Test that whitespace-only strings are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_non_empty_string("   ", "shape_name")
        assert "empty" in str(exc_info.value).lower()
    
    def test_max_length_enforced(self):
        """Test that maximum length is enforced."""
        with pytest.raises(ValidationError) as exc_info:
            validate_non_empty_string("a" * 2050, "shape_name", max_length=2048)
        assert "2048" in str(exc_info.value)
    
    def test_non_string_rejected(self):
        """Test that non-string values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_non_empty_string(123, "shape_name")
        assert "string" in str(exc_info.value).lower()


class TestPydanticModels:
    """Tests for Pydantic validation models."""
    
    def test_graph_uri_model_valid(self):
        """Test GraphUriModel with valid input."""
        model = GraphUriModel(graph_uri="http://ex.org/ShapesGraph")
        assert model.graph_uri == "http://ex.org/ShapesGraph"
    
    def test_graph_uri_model_invalid(self):
        """Test GraphUriModel with invalid input."""
        from pydantic import ValidationError as PydanticValidationError
        with pytest.raises(PydanticValidationError):
            GraphUriModel(graph_uri="invalid")
    
    def test_limit_offset_model_valid(self):
        """Test LimitOffsetModel with valid input."""
        model = LimitOffsetModel(limit=10, offset=0)
        assert model.limit == 10
        assert model.offset == 0
    
    def test_limit_offset_model_optional(self):
        """Test LimitOffsetModel with optional values."""
        model = LimitOffsetModel(limit=None, offset=None)
        assert model.limit is None
        assert model.offset is None
    
    def test_node_shape_name_model_valid(self):
        """Test NodeShapeNameModel with valid input."""
        model = NodeShapeNameModel(node_shape="http://ex.org/PersonShape")
        assert model.node_shape == "http://ex.org/PersonShape"
