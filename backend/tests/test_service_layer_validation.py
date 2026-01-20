"""
Test suite for service layer validation

This module tests that service layer functions properly validate their inputs
before executing queries, ensuring they fail fast with clear error messages.
"""

import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators import ValidationError
from functions.entity_retrieval import (
    get_all_shapes_names,
    get_all_focus_node_names,
    get_all_property_path_names,
    get_all_constraint_components_names,
    get_violations_for_shape_name,
    get_number_of_shapes_in_shapes_graph,
    get_number_of_violations_in_validation_report
)
from functions.violation_analysis_service import (
    get_violations_per_node_shape,
    get_violations_per_path,
    get_violations_per_focus_node
)
from functions.distribution_analysis_service import distribution_of_violations_per_shape
from functions.shape_retrieval import map_property_shapes_to_node_shapes


class TestEntityRetrievalValidation:
    """Test validation in entity_retrieval.py service functions."""
    
    def test_get_all_shapes_names_invalid_uri(self):
        """Test that get_all_shapes_names rejects invalid URIs."""
        # Test with dangerous characters
        with pytest.raises(ValidationError, match="dangerous characters"):
            get_all_shapes_names("http://example.org/test<script>")
        
        # Test with SPARQL keywords
        with pytest.raises(ValidationError, match="SPARQL keywords"):
            get_all_shapes_names("http://example.org/SELECT * FROM")
        
        # Test with invalid format
        with pytest.raises(ValidationError, match="valid HTTP"):
            get_all_shapes_names("not-a-valid-uri")
    
    def test_get_all_focus_node_names_invalid_uri(self):
        """Test that get_all_focus_node_names rejects invalid URIs."""
        with pytest.raises(ValidationError):
            get_all_focus_node_names("invalid://uri<>")
    
    def test_get_all_property_path_names_invalid_uri(self):
        """Test that get_all_property_path_names rejects invalid URIs."""
        with pytest.raises(ValidationError):
            get_all_property_path_names("")
    
    def test_get_all_constraint_components_names_invalid_uri(self):
        """Test that get_all_constraint_components_names rejects invalid URIs."""
        with pytest.raises(ValidationError):
            get_all_constraint_components_names("http://ex.org/test{malicious}")
    
    def test_get_violations_for_shape_name_invalid_shape(self):
        """Test that get_violations_for_shape_name validates shape_name."""
        # Test with invalid shape_name type
        with pytest.raises(ValidationError, match="shape_name must be a string"):
            get_violations_for_shape_name(12345)
        
        # Test with invalid URI in shape_name
        with pytest.raises(ValidationError):
            get_violations_for_shape_name("not-a-uri")
    
    def test_get_violations_for_shape_name_invalid_graph_uri(self):
        """Test that get_violations_for_shape_name validates graph_uri."""
        with pytest.raises(ValidationError):
            get_violations_for_shape_name(
                "http://example.org/Shape",
                graph_uri="invalid<>uri"
            )
    
    def test_get_number_of_shapes_in_shapes_graph_invalid_uri(self):
        """Test that get_number_of_shapes_in_shapes_graph validates URI."""
        with pytest.raises(ValidationError):
            get_number_of_shapes_in_shapes_graph("javascript:alert(1)")
    
    def test_get_number_of_violations_invalid_uri(self):
        """Test that get_number_of_violations_in_validation_report validates URI."""
        with pytest.raises(ValidationError):
            get_number_of_violations_in_validation_report("DROP TABLE users--")


class TestViolationAnalysisValidation:
    """Test validation in violation_analysis_service.py service functions."""
    
    def test_get_violations_per_node_shape_invalid_shapes_graph(self):
        """Test that get_violations_per_node_shape validates shapes_graph_uri."""
        with pytest.raises(ValidationError):
            get_violations_per_node_shape(shapes_graph_uri="<invalid>")
    
    def test_get_violations_per_node_shape_invalid_report_uri(self):
        """Test that get_violations_per_node_shape validates validation_report_uri."""
        with pytest.raises(ValidationError):
            get_violations_per_node_shape(
                shapes_graph_uri="http://ex.org/ShapesGraph",
                validation_report_uri="ftp://invalid"
            )
    
    def test_get_violations_per_path_invalid_uri(self):
        """Test that get_violations_per_path validates URI."""
        with pytest.raises(ValidationError):
            get_violations_per_path("/*malicious*/")
    
    def test_get_violations_per_focus_node_invalid_uri(self):
        """Test that get_violations_per_focus_node validates URI."""
        with pytest.raises(ValidationError):
            get_violations_per_focus_node("--comment")


class TestDistributionAnalysisValidation:
    """Test validation in distribution_analysis_service.py service functions."""
    
    def test_distribution_of_violations_per_shape_invalid_shapes_graph(self):
        """Test that distribution_of_violations_per_shape validates shapes_graph_uri."""
        with pytest.raises(ValidationError):
            distribution_of_violations_per_shape(shapes_graph_uri="|\nbaduri")
    
    def test_distribution_of_violations_per_shape_invalid_report_uri(self):
        """Test that distribution_of_violations_per_shape validates validation_report_uri."""
        with pytest.raises(ValidationError):
            distribution_of_violations_per_shape(
                shapes_graph_uri="http://ex.org/ShapesGraph",
                validation_report_uri="http://ex.org/test\n\rmalicious"
            )


class TestShapeRetrievalValidation:
    """Test validation in shape_retrieval.py service functions."""
    
    def test_map_property_shapes_to_node_shapes_invalid_validation_uri(self):
        """Test that map_property_shapes_to_node_shapes validates validation_report_uri."""
        with pytest.raises(ValidationError):
            map_property_shapes_to_node_shapes(validation_report_uri="^baduri")
    
    def test_map_property_shapes_to_node_shapes_invalid_shapes_uri(self):
        """Test that map_property_shapes_to_node_shapes validates shapes_graph_uri."""
        with pytest.raises(ValidationError):
            map_property_shapes_to_node_shapes(
                validation_report_uri="http://ex.org/ValidationReport",
                shapes_graph_uri="`backdoor`"
            )


class TestValidationErrorMessages:
    """Test that validation error messages are clear and helpful."""
    
    def test_error_message_clarity(self):
        """Test that validation errors have clear, actionable messages."""
        try:
            get_all_shapes_names("http://example.org/SELECT")
            pytest.fail("Should have raised ValidationError")
        except ValidationError as e:
            error_message = str(e)
            assert "SPARQL" in error_message or "invalid" in error_message.lower()
            assert len(error_message) > 10  # Should be descriptive
    
    def test_empty_uri_error(self):
        """Test that empty URIs produce clear error messages."""
        with pytest.raises(ValidationError, match="at least 1 character"):
            get_all_shapes_names("")
    
    def test_too_long_uri_error(self):
        """Test that overly long URIs are rejected."""
        very_long_uri = "http://example.org/" + "a" * 3000
        with pytest.raises(ValidationError, match="at most 2048 characters"):
            get_all_shapes_names(very_long_uri)


class TestValidationWithValidInputs:
    """Test that valid inputs pass validation without errors."""
    
    def test_valid_http_uri(self, mocker):
        """Test that valid HTTP URIs pass validation."""
        # Mock the executor to avoid actual SPARQL queries
        mock_executor = mocker.Mock()
        mock_executor.execute_query.return_value = {"results": {"bindings": []}}
        
        # Should not raise any exception
        result = get_all_shapes_names(
            "http://example.org/ValidGraph",
            executor=mock_executor
        )
        assert isinstance(result, list)
    
    def test_valid_https_uri(self, mocker):
        """Test that valid HTTPS URIs pass validation."""
        mock_executor = mocker.Mock()
        mock_executor.execute_query.return_value = {"results": {"bindings": []}}
        
        # Should not raise any exception
        result = get_all_focus_node_names(
            "https://example.org/SecureGraph",
            executor=mock_executor
        )
        assert isinstance(result, list)
    
    def test_valid_uri_with_path(self, mocker):
        """Test that valid URIs with paths pass validation."""
        mock_executor = mocker.Mock()
        mock_executor.execute_query.return_value = {"results": {"bindings": []}}
        
        # Should not raise any exception
        result = get_all_property_path_names(
            "http://example.org/graphs/validation/report",
            executor=mock_executor
        )
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
