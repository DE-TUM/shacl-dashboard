"""
Unit tests for error_codes module.
Tests for standardized error codes and formatting.
"""
import pytest
from error_codes import (
    ErrorCodes, 
    ERROR_MESSAGES, 
    format_error_response, 
    get_http_status_for_error_code
)


class TestErrorCodes:
    """Test ErrorCodes constants"""
    
    def test_validation_error_codes_exist(self):
        """Should have validation error codes"""
        assert hasattr(ErrorCodes, 'VAL_INVALID_URI')
        assert hasattr(ErrorCodes, 'VAL_INVALID_PARAMETER')
        assert hasattr(ErrorCodes, 'VAL_MISSING_PARAMETER')
        assert hasattr(ErrorCodes, 'VAL_INVALID_FORMAT')
        assert hasattr(ErrorCodes, 'VAL_OUT_OF_RANGE')
    
    def test_resource_error_codes_exist(self):
        """Should have resource error codes"""
        assert hasattr(ErrorCodes, 'RES_GRAPH_NOT_FOUND')
        assert hasattr(ErrorCodes, 'RES_SHAPE_NOT_FOUND')
        assert hasattr(ErrorCodes, 'RES_VIOLATION_NOT_FOUND')
        assert hasattr(ErrorCodes, 'RES_REPORT_NOT_FOUND')
    
    def test_query_error_codes_exist(self):
        """Should have query error codes"""
        assert hasattr(ErrorCodes, 'QRY_EXECUTION_FAILED')
        assert hasattr(ErrorCodes, 'QRY_TIMEOUT')
        assert hasattr(ErrorCodes, 'QRY_INVALID_SYNTAX')
        assert hasattr(ErrorCodes, 'QRY_CONNECTION_ERROR')
    
    def test_system_error_codes_exist(self):
        """Should have system error codes"""
        assert hasattr(ErrorCodes, 'SYS_INTERNAL_ERROR')
        assert hasattr(ErrorCodes, 'SYS_SERVICE_UNAVAILABLE')
        assert hasattr(ErrorCodes, 'SYS_CONFIGURATION_ERROR')
    
    def test_security_error_codes_exist(self):
        """Should have security error codes"""
        assert hasattr(ErrorCodes, 'SEC_INJECTION_DETECTED')
        assert hasattr(ErrorCodes, 'SEC_UNAUTHORIZED')
        assert hasattr(ErrorCodes, 'SEC_FORBIDDEN')


class TestErrorMessages:
    """Test ERROR_MESSAGES dictionary"""
    
    def test_all_error_codes_have_messages(self):
        """Should have message for every error code"""
        error_code_attrs = [attr for attr in dir(ErrorCodes) 
                           if not attr.startswith('_')]
        
        for attr in error_code_attrs:
            code = getattr(ErrorCodes, attr)
            assert code in ERROR_MESSAGES, f"Missing message for {code}"
    
    def test_messages_are_user_friendly(self):
        """Should have user-friendly messages"""
        for code, message in ERROR_MESSAGES.items():
            assert len(message) > 0, f"Empty message for {code}"
            assert not message.startswith('Error:'), f"Message for {code} starts with 'Error:'"
            # Should not contain technical jargon like "exception" or "traceback"
            assert 'exception' not in message.lower()
            assert 'traceback' not in message.lower()


class TestFormatErrorResponse:
    """Test format_error_response function"""
    
    def test_formats_basic_error(self):
        """Should format basic error without details"""
        response = format_error_response(ErrorCodes.SYS_INTERNAL_ERROR)
        
        assert 'error_code' in response
        assert 'message' in response
        assert response['error_code'] == ErrorCodes.SYS_INTERNAL_ERROR
        assert len(response['message']) > 0
    
    def test_formats_error_with_details(self):
        """Should format error with parameter substitution"""
        response = format_error_response(
            ErrorCodes.VAL_INVALID_PARAMETER,
            {'param': 'limit', 'details': 'Must be positive'}
        )
        
        assert response['error_code'] == ErrorCodes.VAL_INVALID_PARAMETER
        assert 'limit' in response['message']
        assert 'Must be positive' in response['message']
    
    def test_handles_missing_format_keys_gracefully(self):
        """Should handle missing format keys without crashing"""
        response = format_error_response(
            ErrorCodes.VAL_INVALID_PARAMETER,
            {'wrong_key': 'value'}
        )
        
        assert 'error_code' in response
        assert 'message' in response
        # Should return message with placeholders intact
        assert '{param}' in response['message']
    
    def test_handles_unknown_error_code(self):
        """Should fallback to internal error for unknown codes"""
        response = format_error_response('UNKNOWN_CODE')
        
        assert response['error_code'] == 'UNKNOWN_CODE'
        assert response['message'] == ERROR_MESSAGES[ErrorCodes.SYS_INTERNAL_ERROR]
    
    def test_response_structure(self):
        """Should return dict with correct structure"""
        response = format_error_response(ErrorCodes.VAL_INVALID_URI)
        
        assert isinstance(response, dict)
        assert set(response.keys()) == {'error_code', 'message'}


class TestGetHttpStatusForErrorCode:
    """Test get_http_status_for_error_code function"""
    
    def test_validation_errors_return_400(self):
        """Should return 400 for validation errors"""
        assert get_http_status_for_error_code(ErrorCodes.VAL_INVALID_URI) == 400
        assert get_http_status_for_error_code(ErrorCodes.VAL_INVALID_PARAMETER) == 400
        assert get_http_status_for_error_code(ErrorCodes.VAL_MISSING_PARAMETER) == 400
    
    def test_resource_errors_return_404(self):
        """Should return 404 for resource errors"""
        assert get_http_status_for_error_code(ErrorCodes.RES_GRAPH_NOT_FOUND) == 404
        assert get_http_status_for_error_code(ErrorCodes.RES_SHAPE_NOT_FOUND) == 404
        assert get_http_status_for_error_code(ErrorCodes.RES_REPORT_NOT_FOUND) == 404
    
    def test_security_errors_return_403(self):
        """Should return 403 for security errors"""
        assert get_http_status_for_error_code(ErrorCodes.SEC_INJECTION_DETECTED) == 403
        assert get_http_status_for_error_code(ErrorCodes.SEC_UNAUTHORIZED) == 403
        assert get_http_status_for_error_code(ErrorCodes.SEC_FORBIDDEN) == 403
    
    def test_query_errors_return_500(self):
        """Should return 500 for query errors"""
        assert get_http_status_for_error_code(ErrorCodes.QRY_EXECUTION_FAILED) == 500
        assert get_http_status_for_error_code(ErrorCodes.QRY_TIMEOUT) == 500
        assert get_http_status_for_error_code(ErrorCodes.QRY_CONNECTION_ERROR) == 500
    
    def test_system_errors_return_500(self):
        """Should return 500 for system errors"""
        assert get_http_status_for_error_code(ErrorCodes.SYS_INTERNAL_ERROR) == 500
        assert get_http_status_for_error_code(ErrorCodes.SYS_SERVICE_UNAVAILABLE) == 500
        assert get_http_status_for_error_code(ErrorCodes.SYS_CONFIGURATION_ERROR) == 500
    
    def test_unknown_code_returns_500(self):
        """Should return 500 for unknown error codes"""
        assert get_http_status_for_error_code('UNKNOWN_CODE') == 500


class TestIntegration:
    """Integration tests for error code system"""
    
    def test_full_error_flow(self):
        """Should create complete error response with proper status"""
        error_code = ErrorCodes.VAL_INVALID_URI
        details = {'param': 'graph_uri'}
        
        response = format_error_response(error_code, details)
        status = get_http_status_for_error_code(error_code)
        
        assert response['error_code'] == error_code
        assert 'URI' in response['message']
        assert status == 400
    
    def test_error_response_serializable(self):
        """Should create JSON-serializable responses"""
        import json
        
        response = format_error_response(ErrorCodes.VAL_INVALID_PARAMETER)
        json_str = json.dumps(response)
        
        assert isinstance(json_str, str)
        assert len(json_str) > 0
