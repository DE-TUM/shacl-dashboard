from flask import Flask, send_file, abort
import os
import subprocess

# Resolve STATIC_FOLDER to an absolute path
STATIC_FOLDER = os.path.abspath(os.path.join('src', 'service', 'frontend'))
VUE_SOURCE_FOLDER = os.path.abspath('.')

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')  # Use the build output folder as the static folder

# Function to build the frontend (Vue.js)
def build_frontend():
    print("Checking if frontend needs to be built...")
    index_path = os.path.join(STATIC_FOLDER, 'index.html')  # Use absolute STATIC_FOLDER
    if not os.path.exists(index_path):
        print("Building the Vue.js frontend...")
        try:
            subprocess.check_call(["npm", "install"], cwd=VUE_SOURCE_FOLDER)
            subprocess.check_call(["npm", "run", "build"], cwd=VUE_SOURCE_FOLDER)
            print("Frontend built successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error building frontend: {e}")
            raise

# Serve the frontend (index.html) for root and any unmatched routes
@app.route('/')
def serve_index():
    index_path = os.path.join(STATIC_FOLDER, 'index.html')
    print("Resolved STATIC_FOLDER:", STATIC_FOLDER)
    print("Resolved index_path:", index_path)
    if os.path.exists(index_path):
        return send_file(index_path)
    else:
        print(f"File not found: {index_path}")
        abort(404)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
