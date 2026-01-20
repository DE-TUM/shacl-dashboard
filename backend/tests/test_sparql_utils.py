"""
Unit tests for sparql_utils module.
Tests for SPARQL result binding extraction utilities.
"""
import pytest
from sparql_utils import (
    safe_get_binding_value,
    safe_get_binding_int,
    safe_get_binding_float,
    safe_get_all_binding_values
)


class TestSafeGetBindingValue:
    """Test safe_get_binding_value function"""
    
    def test_extracts_value_successfully(self):
        """Should extract value from valid binding"""
        bindings = [{"count": {"value": "42", "type": "literal"}}]
        result = safe_get_binding_value(bindings, 0, "count")
        assert result == "42"
    
    def test_returns_default_for_empty_bindings(self):
        """Should return default when bindings list is empty"""
        result = safe_get_binding_value([], 0, "count", default="N/A")
        assert result == "N/A"
    
    def test_returns_default_for_none_bindings(self):
        """Should return default when bindings is None"""
        result = safe_get_binding_value(None, 0, "count", default=0)
        assert result == 0
    
    def test_returns_default_for_out_of_bounds_index(self):
        """Should return default when index is out of bounds"""
        bindings = [{"count": {"value": "42"}}]
        result = safe_get_binding_value(bindings, 10, "count", default=-1)
        assert result == -1
    
    def test_returns_default_for_missing_key(self):
        """Should return default when key doesn't exist"""
        bindings = [{"count": {"value": "42"}}]
        result = safe_get_binding_value(bindings, 0, "missing", default="default")
        assert result == "default"
    
    def test_returns_default_for_missing_value_key(self):
        """Should return default when value_key doesn't exist"""
        bindings = [{"count": {"type": "literal"}}]
        result = safe_get_binding_value(bindings, 0, "count", value_key="value", default=None)
        assert result is None
    
    def test_uses_custom_value_key(self):
        """Should extract using custom value_key"""
        bindings = [{"count": {"value": "42", "type": "literal"}}]
        result = safe_get_binding_value(bindings, 0, "count", value_key="type")
        assert result == "literal"
    
    def test_handles_multiple_bindings(self):
        """Should extract from specified index in multiple bindings"""
        bindings = [
            {"name": {"value": "Alice"}},
            {"name": {"value": "Bob"}},
            {"name": {"value": "Charlie"}}
        ]
        assert safe_get_binding_value(bindings, 0, "name") == "Alice"
        assert safe_get_binding_value(bindings, 1, "name") == "Bob"
        assert safe_get_binding_value(bindings, 2, "name") == "Charlie"
    
    def test_handles_none_default(self):
        """Should properly handle None as default value"""
        result = safe_get_binding_value([], 0, "key")
        assert result is None
    
    def test_handles_malformed_binding_structure(self):
        """Should return default for malformed binding structure"""
        bindings = [{"count": "not_a_dict"}]
        result = safe_get_binding_value(bindings, 0, "count", default="error")
        assert result == "error"


class TestSafeGetBindingInt:
    """Test safe_get_binding_int function"""
    
    def test_extracts_int_successfully(self):
        """Should extract and convert string to int"""
        bindings = [{"count": {"value": "42"}}]
        result = safe_get_binding_int(bindings, 0, "count")
        assert result == 42
        assert isinstance(result, int)
    
    def test_returns_default_for_empty_bindings(self):
        """Should return default int for empty bindings"""
        result = safe_get_binding_int([], 0, "count", default=10)
        assert result == 10
    
    def test_returns_default_for_missing_key(self):
        """Should return default int for missing key"""
        bindings = [{"other": {"value": "42"}}]
        result = safe_get_binding_int(bindings, 0, "count", default=5)
        assert result == 5
    
    def test_returns_default_for_invalid_int(self):
        """Should return default for non-numeric value"""
        bindings = [{"count": {"value": "invalid"}}]
        result = safe_get_binding_int(bindings, 0, "count", default=0)
        assert result == 0
    
    def test_handles_negative_integers(self):
        """Should handle negative integer values"""
        bindings = [{"count": {"value": "-42"}}]
        result = safe_get_binding_int(bindings, 0, "count")
        assert result == -42
    
    def test_handles_zero(self):
        """Should handle zero value"""
        bindings = [{"count": {"value": "0"}}]
        result = safe_get_binding_int(bindings, 0, "count")
        assert result == 0
    
    def test_uses_zero_as_default_by_default(self):
        """Should use 0 as default when not specified"""
        result = safe_get_binding_int([], 0, "count")
        assert result == 0
    
    def test_handles_large_integers(self):
        """Should handle large integer values"""
        bindings = [{"count": {"value": "999999999"}}]
        result = safe_get_binding_int(bindings, 0, "count")
        assert result == 999999999


class TestSafeGetBindingFloat:
    """Test safe_get_binding_float function"""
    
    def test_extracts_float_successfully(self):
        """Should extract and convert string to float"""
        bindings = [{"average": {"value": "3.14"}}]
        result = safe_get_binding_float(bindings, 0, "average")
        assert result == 3.14
        assert isinstance(result, float)
    
    def test_returns_default_for_empty_bindings(self):
        """Should return default float for empty bindings"""
        result = safe_get_binding_float([], 0, "average", default=1.5)
        assert result == 1.5
    
    def test_returns_default_for_missing_key(self):
        """Should return default float for missing key"""
        bindings = [{"other": {"value": "3.14"}}]
        result = safe_get_binding_float(bindings, 0, "average", default=2.5)
        assert result == 2.5
    
    def test_returns_default_for_invalid_float(self):
        """Should return default for non-numeric value"""
        bindings = [{"average": {"value": "invalid"}}]
        result = safe_get_binding_float(bindings, 0, "average", default=0.0)
        assert result == 0.0
    
    def test_handles_negative_floats(self):
        """Should handle negative float values"""
        bindings = [{"average": {"value": "-3.14"}}]
        result = safe_get_binding_float(bindings, 0, "average")
        assert result == -3.14
    
    def test_handles_integer_as_float(self):
        """Should convert integer strings to float"""
        bindings = [{"average": {"value": "42"}}]
        result = safe_get_binding_float(bindings, 0, "average")
        assert result == 42.0
        assert isinstance(result, float)
    
    def test_uses_zero_as_default_by_default(self):
        """Should use 0.0 as default when not specified"""
        result = safe_get_binding_float([], 0, "average")
        assert result == 0.0
    
    def test_handles_scientific_notation(self):
        """Should handle scientific notation"""
        bindings = [{"average": {"value": "1.23e-4"}}]
        result = safe_get_binding_float(bindings, 0, "average")
        assert result == 0.000123


class TestSafeGetAllBindingValues:
    """Test safe_get_all_binding_values function"""
    
    def test_extracts_all_values(self):
        """Should extract values from all bindings"""
        bindings = [
            {"name": {"value": "Alice"}},
            {"name": {"value": "Bob"}},
            {"name": {"value": "Charlie"}}
        ]
        result = safe_get_all_binding_values(bindings, "name")
        assert result == ["Alice", "Bob", "Charlie"]
    
    def test_skips_missing_keys(self):
        """Should skip bindings without the specified key"""
        bindings = [
            {"name": {"value": "Alice"}},
            {"other": {"value": "Skip"}},
            {"name": {"value": "Bob"}}
        ]
        result = safe_get_all_binding_values(bindings, "name")
        assert result == ["Alice", "Bob"]
    
    def test_returns_empty_list_for_no_matches(self):
        """Should return empty list when key not found"""
        bindings = [
            {"other": {"value": "Value1"}},
            {"other": {"value": "Value2"}}
        ]
        result = safe_get_all_binding_values(bindings, "name")
        assert result == []
    
    def test_returns_empty_list_for_empty_bindings(self):
        """Should return empty list for empty bindings"""
        result = safe_get_all_binding_values([], "name")
        assert result == []
    
    def test_uses_custom_value_key(self):
        """Should extract using custom value_key"""
        bindings = [
            {"item": {"value": "Alice", "type": "string"}},
            {"item": {"value": "42", "type": "integer"}},
        ]
        result = safe_get_all_binding_values(bindings, "item", value_key="type")
        assert result == ["string", "integer"]
    
    def test_handles_mixed_valid_invalid_bindings(self):
        """Should extract only valid values"""
        bindings = [
            {"name": {"value": "Alice"}},
            {"name": "invalid"},
            {"name": {"value": "Bob"}},
            None,
            {"name": {"value": "Charlie"}}
        ]
        result = safe_get_all_binding_values(bindings, "name")
        assert "Alice" in result
        assert "Bob" in result
        assert "Charlie" in result
    
    def test_preserves_order(self):
        """Should preserve order of values"""
        bindings = [
            {"num": {"value": "1"}},
            {"num": {"value": "2"}},
            {"num": {"value": "3"}},
            {"num": {"value": "4"}}
        ]
        result = safe_get_all_binding_values(bindings, "num")
        assert result == ["1", "2", "3", "4"]
