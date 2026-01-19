from flask import Blueprint, request, jsonify
from functions import load_graphs
from error_handlers import handle_api_errors, ValidationError

# Define a Blueprint for landing-related routes
landing_bp = Blueprint('landing', __name__)

# Route to load graphs
@landing_bp.route('/load-graphs', methods=['POST'])
@handle_api_errors
def load_graphs_route():
    """
    Load SHACL shapes and validation reports into the Virtuoso database.
    
    This endpoint accepts JSON data specifying file paths and loads the 
    RDF data into named graphs in Virtuoso.
    
    Request JSON body:
    {
        "directory": "directory/path",
        "shapes_file": "shapes.ttl",
        "report_file": "report.ttl"
    }
    
    Returns:
        200 OK: Graphs loaded successfully
        400 Bad Request: Missing parameters or invalid inputs
        500 Server Error: Database error or loading failure
    """
    # Parse JSON request data
    data = request.get_json()

    # Validate input data
    directory = data.get("directory")
    shapes_file = data.get("shapes_file")
    report_file = data.get("report_file")

    if not all([directory, shapes_file, report_file]):
        raise ValidationError('directory, shapes_file, and report_file are required')

    # Call the load_graphs function
    load_graphs(directory, shapes_file, report_file)

    # Return success response
    return jsonify({'message': 'Graphs loaded successfully'}), 200
