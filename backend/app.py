from flask import Flask, send_file, abort
from flask_cors import CORS
import os
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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

# Register blueprints for API routes with version prefix
from routes import blueprints
for blueprint in blueprints:
    app.register_blueprint(blueprint, url_prefix='/api/v1')

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
