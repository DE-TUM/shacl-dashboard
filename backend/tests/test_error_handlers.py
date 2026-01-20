"""
Unit tests for error_handlers module.
Tests for error handling decorators and utilities.
"""
import pytest
from unittest.mock import Mock
from flask import Flask, jsonify
from error_handlers import handle_api_errors, ValidationError
from werkzeug.exceptions import BadRequest


@pytest.fixture
def app():
    """Create test Flask application"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


class TestHandleApiErrorsDecorator:
    """Test handle_api_errors decorator"""
    
    def test_returns_success_response(self, app):
        """Should return success response when no error occurs"""
        @handle_api_errors
        def test_route():
            return jsonify({"result": "success"}), 200
        
        with app.app_context():
            response, status = test_route()
            assert status == 200
            data = response.get_json()
            assert data["result"] == "success"
    
    def test_catches_validation_error(self, app):
        """Should catch ValidationError and return 400"""
        @handle_api_errors
        def test_route():
            raise ValidationError(
                "Invalid input",
                error_code="VAL_INVALID_URI",
                details={}
            )
        
        with app.app_context():
            response, status = test_route()
            assert status == 400
            data = response.get_json()
            assert "error_code" in data
            assert "message" in data
            assert data["error_code"] == "VAL_INVALID_URI"
    
    def test_catches_bad_request(self, app):
        """Should catch BadRequest and return error"""
        @handle_api_errors
        def test_route():
            raise BadRequest("Bad request")
        
        with app.app_context():
            response, status = test_route()
            assert status in [400, 500]
            data = response.get_json()
            assert "error_code" in data or "error" in data
            assert "message" in data or "error" in data
    
    def test_catches_generic_exception(self, app):
        """Should catch generic exceptions and return 500"""
        @handle_api_errors
        def test_route():
            raise Exception("Something went wrong")
        
        with app.app_context():
            response, status = test_route()
            assert status == 500
            data = response.get_json()
            assert "error_code" in data
            assert "message" in data
            assert data["error_code"] == "SYS_INTERNAL_ERROR"
    
    def test_preserves_function_metadata(self, app):
        """Should preserve function name and docstring"""
        @handle_api_errors
        def test_function():
            """Test docstring"""
            return "result"
        
        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test docstring"
    
    def test_handles_runtime_error(self, app):
        """Should catch RuntimeError and return appropriate status"""
        @handle_api_errors
        def test_route():
            raise RuntimeError("Runtime error occurred")
        
        with app.app_context():
            response, status = test_route()
            assert status == 500
            data = response.get_json()
            assert "error_code" in data
            assert "message" in data
            assert data["error_code"] == "SYS_INTERNAL_ERROR"


class TestValidationError:
    """Test ValidationError exception class"""
    
    def test_can_be_raised(self):
        """Should be able to raise ValidationError"""
        with pytest.raises(ValidationError):
            raise ValidationError("Test error")
    
    def test_error_message(self):
        """Should preserve error message"""
        try:
            raise ValidationError("Custom error message")
        except ValidationError as e:
            assert str(e) == "Custom error message"
    
    def test_is_exception_subclass(self):
        """Should be a subclass of Exception"""
        assert issubclass(ValidationError, Exception)
    
    def test_can_be_caught_as_exception(self):
        """Should be catchable as generic Exception"""
        try:
            raise ValidationError("Test")
        except Exception as e:
            assert isinstance(e, ValidationError)
