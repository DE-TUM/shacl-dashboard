# config.py
import os
from typing import List, Dict, Any


class Config:
    """
    Configuration class for SHACL Dashboard backend.
    
    Centralizes all configuration values with validation and environment variable support.
    Provides a single source of truth for application settings.
    """
    
    # SPARQL endpoint configuration
    ENDPOINT_URL: str = "http://localhost:8890/sparql"
    
    # Authentication settings (if needed)
    AUTH_REQUIRED: bool = False
    USERNAME: str = ""
    PASSWORD: str = ""
    
    # Virtuoso ISQL Configuration
    ISQL_PORT: str = os.getenv("VIRTUOSO_ISQL_PORT", "1111")
    ISQL_USERNAME: str = os.getenv("VIRTUOSO_USERNAME", "dba")
    ISQL_PASSWORD: str = os.getenv("VIRTUOSO_PASSWORD", "dba")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    
    # HTTP Status Codes
    HTTP_OK: int = 200
    HTTP_BAD_REQUEST: int = 400
    HTTP_FORBIDDEN: int = 403
    HTTP_NOT_FOUND: int = 404
    HTTP_INTERNAL_SERVER_ERROR: int = 500
    
    # Server Configuration
    DEFAULT_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    DEFAULT_PORT: int = int(os.getenv("FLASK_PORT", "80"))
    DEBUG_MODE: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    USE_JSON_LOGGING: bool = os.getenv("USE_JSON_LOGGING", "false").lower() == "true"  # Enable structured JSON logging for production
    
    # SPARQL Query Configuration
    SPARQL_TIMEOUT: int = int(os.getenv("SPARQL_TIMEOUT", "30"))  # Query timeout in seconds
    SPARQL_MAX_RETRIES: int = int(os.getenv("SPARQL_MAX_RETRIES", "3"))  # Maximum retry attempts
    SPARQL_RETRY_DELAY: float = float(os.getenv("SPARQL_RETRY_DELAY", "1.0"))  # Initial retry delay in seconds
    SPARQL_CONNECTION_POOL_SIZE: int = int(os.getenv("SPARQL_CONNECTION_POOL_SIZE", "5"))  # Connection pool size
    SPARQL_USE_CONNECTION_POOL: bool = os.getenv("SPARQL_USE_CONNECTION_POOL", "true").lower() == "true"  # Enable connection pooling
    
    # Caching Configuration
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"  # Enable query result caching
    CACHE_BACKEND: str = os.getenv("CACHE_BACKEND", "memory")  # Options: 'memory' or 'redis'
    CACHE_DEFAULT_TTL: int = int(os.getenv("CACHE_DEFAULT_TTL", "300"))  # Default cache TTL in seconds (5 minutes)
    CACHE_REDIS_HOST: str = os.getenv("CACHE_REDIS_HOST", "localhost")  # Redis host for caching
    CACHE_REDIS_PORT: int = int(os.getenv("CACHE_REDIS_PORT", "6379"))  # Redis port
    CACHE_REDIS_DB: int = int(os.getenv("CACHE_REDIS_DB", "0"))  # Redis database number
    
    # Metrics Configuration
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"  # Enable Prometheus metrics
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "200 per hour")  # Default rate limit for all routes
    RATE_LIMIT_STORAGE_URL: str = os.getenv("RATE_LIMIT_STORAGE_URL", "memory://")  # Use Redis for production: "redis://localhost:6379"
    
    # Security Headers Configuration
    SECURITY_HEADERS_ENABLED: bool = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
    # Content Security Policy - restrict sources for scripts, styles, etc.
    CSP_POLICY: Dict[str, Any] = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'"],  # Vue.js may need unsafe-inline
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", "data:"],
        'font-src': "'self'",
        'connect-src': "'self'",
        'frame-ancestors': "'none'",
    }
    HSTS_MAX_AGE: int = 31536000  # HTTP Strict Transport Security: 1 year
    HSTS_INCLUDE_SUBDOMAINS: bool = True
    FORCE_HTTPS: bool = os.getenv("FORCE_HTTPS", "false").lower() == "true"  # Set to true in production
    
    # Triple store type - used to handle store-specific operations
    TRIPLE_STORE_TYPE: str = "virtuoso"  # Options: "virtuoso", "fuseki", "stardog", etc.
    
    # Graph URIs
    SHAPES_GRAPH_URI: str = "http://ex.org/ShapesGraph"
    VALIDATION_REPORT_URI: str = "http://ex.org/ValidationReport"
    
    # SHACL Constraints and Features (SHACL Core Constraint Components)
    # Based on W3C SHACL Recommendation: https://www.w3.org/TR/shacl/#core-components
    SHACL_FEATURES: List[str] = [
        # 4.1 Value Type Constraint Components
        "http://www.w3.org/ns/shacl#class",
        "http://www.w3.org/ns/shacl#datatype",
        "http://www.w3.org/ns/shacl#nodeKind",  # Correct SHACL spelling (enforced)
        
        # 4.2 Cardinality Constraint Components
        "http://www.w3.org/ns/shacl#minCount",
        "http://www.w3.org/ns/shacl#maxCount",
        
        # 4.3 Value Range Constraint Components
        "http://www.w3.org/ns/shacl#minExclusive",
        "http://www.w3.org/ns/shacl#minInclusive",
        "http://www.w3.org/ns/shacl#maxExclusive",
        "http://www.w3.org/ns/shacl#maxInclusive",
        
        # 4.4 String-based Constraint Components
        "http://www.w3.org/ns/shacl#minLength",
        "http://www.w3.org/ns/shacl#maxLength",
        "http://www.w3.org/ns/shacl#pattern",
        "http://www.w3.org/ns/shacl#flags",
        "http://www.w3.org/ns/shacl#languageIn",
        "http://www.w3.org/ns/shacl#uniqueLang",
        
        # 4.5 Property Pair Constraint Components
        "http://www.w3.org/ns/shacl#equals",
        "http://www.w3.org/ns/shacl#disjoint",
        "http://www.w3.org/ns/shacl#lessThan",
        "http://www.w3.org/ns/shacl#lessThanOrEquals",
        
        # 4.6 Logical Constraint Components
        "http://www.w3.org/ns/shacl#not",
        "http://www.w3.org/ns/shacl#and",
        "http://www.w3.org/ns/shacl#or",
        "http://www.w3.org/ns/shacl#xone",
        
        # 4.7 Shape-based Constraint Components
        "http://www.w3.org/ns/shacl#node",
        "http://www.w3.org/ns/shacl#qualifiedValueShape",
        "http://www.w3.org/ns/shacl#qualifiedMinCount",
        "http://www.w3.org/ns/shacl#qualifiedMaxCount",
        "http://www.w3.org/ns/shacl#qualifiedValueShapesDisjoint",
        
        # 4.8 Other Constraint Components
        "http://www.w3.org/ns/shacl#closed",
        "http://www.w3.org/ns/shacl#ignoredProperties",
        "http://www.w3.org/ns/shacl#hasValue",
        "http://www.w3.org/ns/shacl#in"
    ]
    
    # Docker-related settings (for Virtuoso)
    DATA_DIR_IN_DOCKER: str = "/data"  # Directory in Docker container
    DOCKER_CONTAINER_NAME: str = "virtuoso"  # Name of the Docker container
    
    # Store-specific configuration
    STORE_CONFIG: Dict[str, Dict[str, Any]] = {
        "virtuoso": {
            "isql_path": "/usr/local/virtuoso-opensource/bin/isql",
            "isql_port": 1111,
            "bulk_load_enabled": True,
        },
        "fuseki": {
            "admin_endpoint": "http://localhost:3030/$/",
            "bulk_load_enabled": False,
        },
        "stardog": {
            "admin_endpoint": "http://localhost:5820",
            "database": "shacldb",
            "bulk_load_enabled": True,
        }
    }
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate configuration values on startup.
        
        Raises:
            ValueError: If any configuration value is invalid
        """
        # Validate endpoint URL
        if not cls.ENDPOINT_URL or not isinstance(cls.ENDPOINT_URL, str):
            raise ValueError("ENDPOINT_URL must be a non-empty string")
        
        if not cls.ENDPOINT_URL.startswith(("http://", "https://")):
            raise ValueError("ENDPOINT_URL must be a valid HTTP(S) URL")
        
        # Validate graph URIs
        for uri_name, uri_value in [("SHAPES_GRAPH_URI", cls.SHAPES_GRAPH_URI), 
                                      ("VALIDATION_REPORT_URI", cls.VALIDATION_REPORT_URI)]:
            if not uri_value or not isinstance(uri_value, str):
                raise ValueError(f"{uri_name} must be a non-empty string")
            if not uri_value.startswith(("http://", "https://")):
                raise ValueError(f"{uri_name} must be a valid HTTP(S) URI")
        
        # Validate port number
        if not isinstance(cls.DEFAULT_PORT, int) or cls.DEFAULT_PORT < 1 or cls.DEFAULT_PORT > 65535:
            raise ValueError("DEFAULT_PORT must be a valid port number (1-65535)")
        
        # Validate SPARQL query configuration
        if not isinstance(cls.SPARQL_TIMEOUT, int) or cls.SPARQL_TIMEOUT < 1:
            raise ValueError("SPARQL_TIMEOUT must be a positive integer")
        
        if not isinstance(cls.SPARQL_MAX_RETRIES, int) or cls.SPARQL_MAX_RETRIES < 0:
            raise ValueError("SPARQL_MAX_RETRIES must be a non-negative integer")
        
        if not isinstance(cls.SPARQL_RETRY_DELAY, (int, float)) or cls.SPARQL_RETRY_DELAY < 0:
            raise ValueError("SPARQL_RETRY_DELAY must be a non-negative number")
        
        # Validate triple store type
        if cls.TRIPLE_STORE_TYPE not in cls.STORE_CONFIG:
            raise ValueError(f"TRIPLE_STORE_TYPE '{cls.TRIPLE_STORE_TYPE}' is not configured")
        
        # Validate SHACL features list
        if not cls.SHACL_FEATURES or not isinstance(cls.SHACL_FEATURES, list):
            raise ValueError("SHACL_FEATURES must be a non-empty list")
        
        # Ensure all SHACL features are valid URIs
        for feature in cls.SHACL_FEATURES:
            if not feature.startswith("http://www.w3.org/ns/shacl#"):
                raise ValueError(f"Invalid SHACL feature URI: {feature}")


# Create module-level constants for backward compatibility
ENDPOINT_URL = Config.ENDPOINT_URL
AUTH_REQUIRED = Config.AUTH_REQUIRED
USERNAME = Config.USERNAME
PASSWORD = Config.PASSWORD
ISQL_PORT = Config.ISQL_PORT
ISQL_USERNAME = Config.ISQL_USERNAME
ISQL_PASSWORD = Config.ISQL_PASSWORD
ALLOWED_ORIGINS = Config.ALLOWED_ORIGINS
HTTP_OK = Config.HTTP_OK
HTTP_BAD_REQUEST = Config.HTTP_BAD_REQUEST
HTTP_FORBIDDEN = Config.HTTP_FORBIDDEN
HTTP_NOT_FOUND = Config.HTTP_NOT_FOUND
HTTP_INTERNAL_SERVER_ERROR = Config.HTTP_INTERNAL_SERVER_ERROR
DEFAULT_HOST = Config.DEFAULT_HOST
DEFAULT_PORT = Config.DEFAULT_PORT
DEBUG_MODE = Config.DEBUG_MODE
LOG_LEVEL = Config.LOG_LEVEL
USE_JSON_LOGGING = Config.USE_JSON_LOGGING
SPARQL_TIMEOUT = Config.SPARQL_TIMEOUT
SPARQL_MAX_RETRIES = Config.SPARQL_MAX_RETRIES
SPARQL_RETRY_DELAY = Config.SPARQL_RETRY_DELAY
SPARQL_CONNECTION_POOL_SIZE = Config.SPARQL_CONNECTION_POOL_SIZE
SPARQL_USE_CONNECTION_POOL = Config.SPARQL_USE_CONNECTION_POOL
CACHE_ENABLED = Config.CACHE_ENABLED
CACHE_BACKEND = Config.CACHE_BACKEND
CACHE_DEFAULT_TTL = Config.CACHE_DEFAULT_TTL
CACHE_REDIS_HOST = Config.CACHE_REDIS_HOST
CACHE_REDIS_PORT = Config.CACHE_REDIS_PORT
CACHE_REDIS_DB = Config.CACHE_REDIS_DB
METRICS_ENABLED = Config.METRICS_ENABLED
RATE_LIMIT_ENABLED = Config.RATE_LIMIT_ENABLED
RATE_LIMIT_DEFAULT = Config.RATE_LIMIT_DEFAULT
RATE_LIMIT_STORAGE_URL = Config.RATE_LIMIT_STORAGE_URL
SECURITY_HEADERS_ENABLED = Config.SECURITY_HEADERS_ENABLED
CSP_POLICY = Config.CSP_POLICY
HSTS_MAX_AGE = Config.HSTS_MAX_AGE
HSTS_INCLUDE_SUBDOMAINS = Config.HSTS_INCLUDE_SUBDOMAINS
FORCE_HTTPS = Config.FORCE_HTTPS
TRIPLE_STORE_TYPE = Config.TRIPLE_STORE_TYPE
SHAPES_GRAPH_URI = Config.SHAPES_GRAPH_URI
VALIDATION_REPORT_URI = Config.VALIDATION_REPORT_URI
SHACL_FEATURES = Config.SHACL_FEATURES
DATA_DIR_IN_DOCKER = Config.DATA_DIR_IN_DOCKER
DOCKER_CONTAINER_NAME = Config.DOCKER_CONTAINER_NAME
STORE_CONFIG = Config.STORE_CONFIG

# Validate configuration on module import
try:
    Config.validate()
except ValueError as e:
    import sys
    print(f"Configuration validation error: {e}", file=sys.stderr)
    # Don't exit - allow the application to start and report the error properly
    # sys.exit(1)