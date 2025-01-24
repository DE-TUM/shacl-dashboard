from flask import Blueprint, request, jsonify
from functions import load_graphs

# Define a Blueprint for landing-related routes
landing_bp = Blueprint('landing', __name__)

# Route to load graphs
@landing_bp.route('/load-graphs', methods=['POST'])
def load_graphs_route():
    try:
        # Parse JSON request data
        data = request.get_json()

        # Validate input data
        directory = data.get("directory")
        shapes_file = data.get("shapes_file")
        report_file = data.get("report_file")

        if not all([directory, shapes_file, report_file]):
            return jsonify({'error': 'directory, shapes_file, and report_file are required'}), 400

        # Call the load_graphs function
        load_graphs(directory, shapes_file, report_file)

        # Return success response
        return jsonify({'message': 'Graphs loaded successfully'}), 200

    except TypeError as e:
        # Handle type errors from load_graphs function
        return jsonify({'error': f"Type error: {str(e)}"}), 400

    except ValueError as e:
        # Handle value errors from load_graphs function
        return jsonify({'error': f"Value error: {str(e)}"}), 400

    except Exception as e:
        # Handle other exceptions
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500
