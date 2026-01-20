"""
Unit tests for config module.
Tests for Config class validation and settings.
"""
import pytest
from config import Config


class TestConfigClass:
    """Test Config class attributes and validation"""
    
    def test_endpoint_url_is_string(self):
        """Should have ENDPOINT_URL as string"""
        assert isinstance(Config.ENDPOINT_URL, str)
        assert Config.ENDPOINT_URL == "http://localhost:8890/sparql"
    
    def test_http_status_codes(self):
        """Should define standard HTTP status codes"""
        assert Config.HTTP_OK == 200
        assert Config.HTTP_BAD_REQUEST == 400
        assert Config.HTTP_FORBIDDEN == 403
        assert Config.HTTP_NOT_FOUND == 404
        assert Config.HTTP_INTERNAL_SERVER_ERROR == 500
    
    def test_sparql_timeout_is_int(self):
        """Should have SPARQL_TIMEOUT as integer"""
        assert isinstance(Config.SPARQL_TIMEOUT, int)
        assert Config.SPARQL_TIMEOUT > 0
    
    def test_sparql_max_retries_is_int(self):
        """Should have SPARQL_MAX_RETRIES as integer"""
        assert isinstance(Config.SPARQL_MAX_RETRIES, int)
        assert Config.SPARQL_MAX_RETRIES >= 0
    
    def test_sparql_retry_delay_is_float(self):
        """Should have SPARQL_RETRY_DELAY as float"""
        assert isinstance(Config.SPARQL_RETRY_DELAY, (int, float))
        assert Config.SPARQL_RETRY_DELAY >= 0
    
    def test_auth_required_is_bool(self):
        """Should have AUTH_REQUIRED as boolean"""
        assert isinstance(Config.AUTH_REQUIRED, bool)
    
    def test_debug_mode_is_bool(self):
        """Should have DEBUG_MODE as boolean"""
        assert isinstance(Config.DEBUG_MODE, bool)
    
    def test_use_json_logging_is_bool(self):
        """Should have USE_JSON_LOGGING as boolean"""
        assert isinstance(Config.USE_JSON_LOGGING, bool)
    
    def test_default_host_is_string(self):
        """Should have DEFAULT_HOST as string"""
        assert isinstance(Config.DEFAULT_HOST, str)
    
    def test_default_port_is_int(self):
        """Should have DEFAULT_PORT as integer"""
        assert isinstance(Config.DEFAULT_PORT, int)
        assert Config.DEFAULT_PORT > 0
        assert Config.DEFAULT_PORT <= 65535
    
    def test_allowed_origins_is_list(self):
        """Should have ALLOWED_ORIGINS as list"""
        assert isinstance(Config.ALLOWED_ORIGINS, list)
    
    def test_log_level_is_valid(self):
        """Should have valid LOG_LEVEL"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert Config.LOG_LEVEL in valid_levels
    
    def test_isql_configuration(self):
        """Should have ISQL configuration"""
        assert isinstance(Config.ISQL_PORT, str)
        assert isinstance(Config.ISQL_USERNAME, str)
        assert isinstance(Config.ISQL_PASSWORD, str)
