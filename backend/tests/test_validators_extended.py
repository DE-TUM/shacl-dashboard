"""
Additional unit tests for validators module.
Tests for edge cases and error conditions.
"""
import pytest
from pydantic import ValidationError as PydanticValidationError
from validators import (
    ValidationError,
    GraphUriModel,
    LimitOffsetModel,
    NodeShapeNameModel,
    validate_graph_uri,
    validate_limit_offset,
    validate_node_shape_uri,
    validate_positive_int,
    validate_non_empty_string
)


class TestValidationErrorException:
    """Test custom ValidationError exception"""
    
    def test_can_be_raised(self):
        """Should be able to raise ValidationError"""
        with pytest.raises(ValidationError):
            raise ValidationError("Test error")
    
    def test_has_message(self):
        """Should preserve error message"""
        try:
            raise ValidationError("Custom message")
        except ValidationError as e:
            assert str(e) == "Custom message"
    
    def test_is_exception_subclass(self):
        """Should be subclass of Exception"""
        assert issubclass(ValidationError, Exception)


class TestGraphUriModelEdgeCases:
    """Test GraphUriModel edge cases"""
    
    def test_rejects_uri_with_newline(self):
        """Should reject URI with newline"""
        with pytest.raises(PydanticValidationError):
            GraphUriModel(graph_uri="http://example.org/\ngraph")
    
    def test_rejects_uri_with_tab(self):
        """Should reject URI with tab character"""
        with pytest.raises(PydanticValidationError):
            GraphUriModel(graph_uri="http://example.org/\tgraph")
    
    def test_rejects_uri_with_carriage_return(self):
        """Should reject URI with carriage return"""
        with pytest.raises(PydanticValidationError):
            GraphUriModel(graph_uri="http://example.org/\rgraph")
    
    def test_rejects_ftp_uri(self):
        """Should reject non-HTTP(S) schemes"""
        with pytest.raises(PydanticValidationError):
            GraphUriModel(graph_uri="ftp://example.org/graph")
    
    def test_rejects_file_uri(self):
        """Should reject file:// URIs"""
        with pytest.raises(PydanticValidationError):
            GraphUriModel(graph_uri="file:///path/to/file")
    
    def test_rejects_uri_with_all_dangerous_chars(self):
        """Should reject URIs with various dangerous characters"""
        dangerous_uris = [
            "http://example.org/<graph>",
            "http://example.org/{graph}",
            "http://example.org/graph|test",
            "http://example.org/graph\\test",
            "http://example.org/graph^test",
            "http://example.org/graph`test"
        ]
        for uri in dangerous_uris:
            with pytest.raises(PydanticValidationError):
                GraphUriModel(graph_uri=uri)
    
    def test_rejects_uri_with_sql_comment(self):
        """Should reject URIs with SQL comment syntax"""
        with pytest.raises(PydanticValidationError):
            GraphUriModel(graph_uri="http://example.org/graph--comment")
    
    def test_rejects_uri_with_c_comment(self):
        """Should reject URIs with C-style comment"""
        with pytest.raises(PydanticValidationError):
            GraphUriModel(graph_uri="http://example.org/graph/*comment*/")


class TestLimitOffsetModelEdgeCases:
    """Test LimitOffsetModel edge cases"""
    
    def test_accepts_both_none(self):
        """Should accept both limit and offset as None"""
        model = LimitOffsetModel(limit=None, offset=None)
        assert model.limit is None
        assert model.offset is None
    
    def test_accepts_limit_only(self):
        """Should accept limit without offset"""
        model = LimitOffsetModel(limit=100)
        assert model.limit == 100
        assert model.offset is None
    
    def test_accepts_offset_only(self):
        """Should accept offset without limit"""
        model = LimitOffsetModel(offset=50)
        assert model.offset == 50
        assert model.limit is None
    
    def test_limit_boundary_10000(self):
        """Should accept limit exactly at 10000"""
        model = LimitOffsetModel(limit=10000)
        assert model.limit == 10000
    
    def test_rejects_limit_over_10000(self):
        """Should reject limit over 10000"""
        with pytest.raises(PydanticValidationError):
            LimitOffsetModel(limit=10001)
    
    def test_offset_can_be_large(self):
        """Should accept large offset values"""
        model = LimitOffsetModel(offset=999999)
        assert model.offset == 999999


class TestNodeShapeNameModelEdgeCases:
    """Test NodeShapeNameModel edge cases"""
    
    def test_rejects_empty_string(self):
        """Should reject empty string"""
        with pytest.raises(PydanticValidationError):
            NodeShapeNameModel(node_shape="")
    
    def test_rejects_whitespace_only(self):
        """Should reject whitespace-only string"""
        with pytest.raises(PydanticValidationError):
            NodeShapeNameModel(node_shape="   ")
    
    def test_rejects_non_http_scheme(self):
        """Should reject non-HTTP(S) URI"""
        with pytest.raises(PydanticValidationError):
            NodeShapeNameModel(node_shape="mailto:test@example.org")
    
    def test_accepts_uri_with_fragment(self):
        """Should accept URI with fragment"""
        model = NodeShapeNameModel(node_shape="http://example.org/shapes#NodeShape1")
        assert "#NodeShape1" in model.node_shape
    
    def test_accepts_uri_with_query_params(self):
        """Should accept URI with query parameters"""
        model = NodeShapeNameModel(node_shape="http://example.org/shapes?id=123")
        assert "?id=123" in model.node_shape


class TestValidateFunctionsErrorMessages:
    """Test that validation functions provide clear error messages"""
    
    def test_validate_graph_uri_custom_param_name_in_message(self):
        """Should include custom parameter name in error message"""
        try:
            validate_graph_uri("", param_name="custom_uri")
        except ValidationError as e:
            assert "custom_uri" in str(e)
    
    def test_validate_positive_int_includes_param_name(self):
        """Should include parameter name in error"""
        try:
            validate_positive_int(-5, param_name="my_value")
        except ValidationError as e:
            assert "my_value" in str(e).lower()
    
    def test_validate_non_empty_string_includes_param_name(self):
        """Should include parameter name in error"""
        try:
            validate_non_empty_string("", param_name="my_string")
        except ValidationError as e:
            assert "my_string" in str(e).lower()


class TestValidatePositiveIntBoundaries:
    """Test validate_positive_int with various boundaries"""
    
    def test_accepts_value_at_min_boundary(self):
        """Should accept value at minimum boundary"""
        result = validate_positive_int(5, min_value=5)
        assert result == 5
    
    def test_accepts_value_at_max_boundary(self):
        """Should accept value at maximum boundary"""
        result = validate_positive_int(100, max_value=100)
        assert result == 100
    
    def test_rejects_value_below_min(self):
        """Should reject value below minimum"""
        with pytest.raises(ValidationError):
            validate_positive_int(4, min_value=5)
    
    def test_rejects_value_above_max(self):
        """Should reject value above maximum"""
        with pytest.raises(ValidationError):
            validate_positive_int(101, max_value=100)
    
    def test_accepts_value_when_no_max(self):
        """Should accept large values when no maximum"""
        result = validate_positive_int(999999, min_value=1)
        assert result == 999999


class TestValidateNonEmptyStringBoundaries:
    """Test validate_non_empty_string with length boundaries"""
    
    def test_accepts_string_at_max_length(self):
        """Should accept string exactly at max length"""
        text = "a" * 100
        result = validate_non_empty_string(text, max_length=100)
        assert result == text
    
    def test_rejects_string_over_max_length(self):
        """Should reject string exceeding max length"""
        text = "a" * 101
        with pytest.raises(ValidationError):
            validate_non_empty_string(text, max_length=100)
    
    def test_trims_whitespace_from_string(self):
        """Should trim leading/trailing whitespace"""
        result = validate_non_empty_string("  test  ")
        assert result == "test"
    
    def test_rejects_only_whitespace_after_trim(self):
        """Should reject string that's only whitespace"""
        with pytest.raises(ValidationError):
            validate_non_empty_string("     ")


class TestValidateLimitOffsetTupleReturn:
    """Test validate_limit_offset returns tuple correctly"""
    
    def test_returns_tuple_with_both_values(self):
        """Should return tuple (limit, offset)"""
        result = validate_limit_offset(limit=10, offset=20)
        assert isinstance(result, tuple)
        assert result == (10, 20)
    
    def test_returns_tuple_with_none_values(self):
        """Should return tuple with None values"""
        result = validate_limit_offset()
        assert result == (None, None)
    
    def test_returns_tuple_with_mixed_values(self):
        """Should handle mix of None and values"""
        result1 = validate_limit_offset(limit=10, offset=None)
        result2 = validate_limit_offset(limit=None, offset=20)
        assert result1 == (10, None)
        assert result2 == (None, 20)
