from flask import Flask, send_file, abort, request, g
from flask_cors import CORS
import os
import subprocess
import uuid
import time

# Import logging configuration
from logging_config import setup_logging, get_logger, set_correlation_id, log_api_request, log_api_response
from config import (
    LOG_LEVEL, USE_JSON_LOGGING, RATE_LIMIT_ENABLED, RATE_LIMIT_DEFAULT, 
    RATE_LIMIT_STORAGE_URL, SECURITY_HEADERS_ENABLED, CSP_POLICY, 
    HSTS_MAX_AGE, HSTS_INCLUDE_SUBDOMAINS, FORCE_HTTPS
)

# Setup structured logging
setup_logging(log_level=LOG_LEVEL, use_json=USE_JSON_LOGGING)
logger = get_logger(__name__)


"""
SHACL Dashboard Backend App

This is the main entry point for the SHACL Dashboard backend Flask application.
It serves both the API endpoints and the static Vue.js frontend files from the 
compiled 'dist' directory.

The app handles:
1. API routes for SHACL validation queries
2. Serving the compiled Vue.js frontend
3. Frontend build process (if necessary)

Usage:
  python app.py  # Starts the Flask server on port 80
"""


# Resolve STATIC_FOLDER to an absolute path

STATIC_FOLDER = os.path.abspath(os.path.join('..', 'frontend', 'dist'))
VUE_SOURCE_FOLDER = os.path.abspath('../frontend')

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')  # Use the build output folder as the static folder

# Enable CORS for frontend-backend communication with specific origins
from config import ALLOWED_ORIGINS
CORS(app, origins=ALLOWED_ORIGINS)

# Configure rate limiting (if enabled)
if RATE_LIMIT_ENABLED:
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[RATE_LIMIT_DEFAULT],
            storage_uri=RATE_LIMIT_STORAGE_URL,
            storage_options={},
            # Exempt health check endpoints from rate limiting
            default_limits_exempt_when=lambda: request.path.startswith('/health')
        )
        logger.info("Rate limiting enabled: %s", RATE_LIMIT_DEFAULT)
    except ImportError:
        logger.warning("Flask-Limiter not installed. Rate limiting disabled.")
    except Exception as e:
        logger.error("Failed to initialize rate limiter: %s", e)

# Configure security headers (if enabled)
if SECURITY_HEADERS_ENABLED:
    try:
        from flask_talisman import Talisman
        
        # Initialize Talisman with security headers
        Talisman(
            app,
            force_https=FORCE_HTTPS,  # Set to True in production
            strict_transport_security=True,
            strict_transport_security_max_age=HSTS_MAX_AGE,
            strict_transport_security_include_subdomains=HSTS_INCLUDE_SUBDOMAINS,
            content_security_policy=CSP_POLICY,
            content_security_policy_nonce_in=['script-src'],
            referrer_policy='strict-origin-when-cross-origin',
            feature_policy={
                'geolocation': "'none'",
                'microphone': "'none'",
                'camera': "'none'",
            },
            # Don't apply to static files served from /assets
            content_security_policy_report_only=False,
        )
        logger.info("Security headers enabled (HTTPS forced: %s)", FORCE_HTTPS)
    except ImportError:
        logger.warning("Flask-Talisman not installed. Security headers disabled.")
    except Exception as e:
        logger.error("Failed to initialize security headers: %s", e)


# Middleware for request correlation IDs and logging
@app.before_request
def before_request():
    """Set up correlation ID and log incoming requests."""
    # Generate or extract correlation ID
    correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
    set_correlation_id(correlation_id)
    g.correlation_id = correlation_id
    g.start_time = time.time()
    
    # Log API requests (exclude static file requests)
    if request.path.startswith('/api/'):
        log_api_request(
            logger,
            method=request.method,
            path=request.path,
            params=request.args.to_dict() if request.args else None
        )


@app.after_request
def after_request(response):
    """Log outgoing responses with execution time and track metrics."""
    # Log API responses and track metrics (exclude static file requests and metrics endpoint)
    if request.path.startswith('/api/') and hasattr(g, 'start_time'):
        execution_time = time.time() - g.start_time
        log_api_response(logger, response.status_code, execution_time)
        
        # Add correlation ID to response headers
        if hasattr(g, 'correlation_id'):
            response.headers['X-Correlation-ID'] = g.correlation_id
        
        # Track metrics (skip metrics endpoint itself)
        if not request.path.endswith('/metrics'):
            try:
                from metrics import get_metrics_manager
                metrics = get_metrics_manager()
                metrics.track_http_request(
                    method=request.method,
                    endpoint=request.path,
                    status=response.status_code,
                    duration=execution_time
                )
            except Exception as e:
                logger.warning("Failed to track metrics: %s", e)
    
    return response


# Register blueprints for API routes with version prefix
from routes import blueprints
for blueprint in blueprints:
    app.register_blueprint(blueprint, url_prefix='/api/v1')

# Register Flask-RESTX API blueprint for Swagger/OpenAPI documentation
from app_api import api_blueprint
app.register_blueprint(api_blueprint)

# Function to build the frontend (Vue.js)
def build_frontend():
    logger.info("Checking if frontend needs to be built...")
    index_path = os.path.join(STATIC_FOLDER, 'index.html')  # Use absolute STATIC_FOLDER
    if not os.path.exists(index_path):
        logger.info("Building the Vue.js frontend...")
        try:
            subprocess.check_call(["npm", "install"], cwd=VUE_SOURCE_FOLDER)
            subprocess.check_call(["npm", "run", "build"], cwd=VUE_SOURCE_FOLDER)
            logger.info("Frontend built successfully.")
        except subprocess.CalledProcessError as e:
            logger.error("Error building frontend: %s", e)
            raise

# Serve the frontend (index.html) for root and any unmatched routes
@app.route('/')
def serve_index():
    index_path = os.path.join(STATIC_FOLDER, 'index.html')
    logger.debug("Resolved STATIC_FOLDER: %s", STATIC_FOLDER)
    logger.debug("Resolved index_path: %s", index_path)
    if os.path.exists(index_path):
        return send_file(index_path)
    else:
        logger.error("File not found: %s", index_path)
        abort(404)

# Catch-all route to serve index.html for Vue Router (must be last)
@app.route('/<path:path>')
def catch_all(path):
    # Check if it's a request for a static file
    file_path = os.path.join(STATIC_FOLDER, path)
    # Resolve absolute paths and check if it's within STATIC_FOLDER
    try:
        file_path = os.path.abspath(file_path)
        static_folder_abs = os.path.abspath(STATIC_FOLDER)
        if not file_path.startswith(static_folder_abs):
            logger.warning("Attempted directory traversal: %s", path)
            abort(403)
    except (ValueError, OSError) as e:
        logger.error("Invalid path: %s", e)
        abort(400)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path)
    # Otherwise, serve index.html for Vue Router
    index_path = os.path.join(STATIC_FOLDER, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    else:
        abort(404)

if __name__ == '__main__':
    from config import DEFAULT_HOST, DEFAULT_PORT, DEBUG_MODE
    app.run(debug=DEBUG_MODE, host=DEFAULT_HOST, port=DEFAULT_PORT)
