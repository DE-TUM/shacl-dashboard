# SHACL Dashboard

A comprehensive visualization and analysis tool for SHACL validation results. SHACL Dashboard helps data engineers and knowledge graph maintainers understand, analyze, and address constraint violations in RDF data.

![SHACL Dashboard Screenshot](docs/images/dashboard-screenshot.png)

## Overview

The SHACL Dashboard provides an interactive web interface for exploring and analyzing SHACL validation results. It connects to a Virtuoso RDF database containing SHACL shapes and validation reports, offering detailed statistics, visualizations, and insights into constraint violations.

## Key Features

- **Interactive Dashboards**: Visualize validation metrics with charts and tables
- **Detailed Analysis**: Examine violations by shapes, paths, focus nodes, and constraint types
- **Comprehensive Statistics**: View distributions and patterns in validation results
- **RESTful API**: Access all validation data programmatically through the API
- **Shape-Specific Analysis**: Dive deep into individual shape validation patterns

## Architecture

SHACL Dashboard follows a client-server architecture:

- **Frontend**: Vue.js 3 single-page application with Vuetify and Chart.js
- **Backend**: Flask RESTful API connecting to Virtuoso database
- **Database**: Virtuoso RDF triple store containing shapes and validation reports

![Architecture Diagram](docs/images/architecture.png)

## Quick Start

### Prerequisites

- Docker and Docker Compose (recommended)
- Alternatively: Node.js 18+, Python 3.8+, and Virtuoso

### Using Docker (Recommended)

```bash
git clone https://github.com/yourusername/shacl-dashboard.git
cd shacl-dashboard
docker-compose up -d
```

The dashboard will be available at http://localhost:80

### Manual Setup

1. Start Virtuoso:

```bash
# Start Virtuoso with your preferred method
# Example using Docker:
docker run --name virtuoso -p 8890:8890 -p 1111:1111 -d openlink/virtuoso-opensource-7
```

Ensure Virtuoso is running and accessible at http://localhost:8890/sparql

2. Set up the Backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# You might need to run with admin privileges since it uses port 80
sudo python app.py  # On Windows: run as Administrator
```

3. Set up the Frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173

## Usage

### Data Setup

#### Configuration Options

SHACL Dashboard's backend uses a centralized configuration file (`backend/config.py`) that allows you to:

- Define your SPARQL endpoint URL
- Set authentication credentials if required
- Configure graph URIs for shapes and validation reports
- Choose the triple store type (Virtuoso, Fuseki, Stardog, etc.)

The default configuration uses:

- SPARQL Endpoint: `http://localhost:8890/sparql`
- Shapes Graph: `http://ex.org/ShapesGraph`
- Validation Report: `http://ex.org/ValidationReport`

#### Using Alternative Triple Stores

By default, SHACL Dashboard is configured to use Virtuoso. However, it supports other SPARQL endpoints:

```python
# For Apache Fuseki
ENDPOINT_URL = "http://localhost:3030/dataset/sparql"
TRIPLE_STORE_TYPE = "fuseki"

# For Stardog
ENDPOINT_URL = "http://localhost:5820/shacldb/query"
AUTH_REQUIRED = True
USERNAME = "admin"
PASSWORD = "admin"
TRIPLE_STORE_TYPE = "stardog"
```

#### Loading Data

You have two main options for loading data:

1. **API Endpoint**: Use the `/api/landing/load-graphs` endpoint to upload files
   ```bash
   curl -X POST http://localhost/api/landing/load-graphs -H "Content-Type: application/json" \
     -d '{"directory": "path/to/data", "shapes_file": "shapes.ttl", "report_file": "report.ttl"}'
   ```

2. **Triple Store Interface**: Upload directly through your triple store's web interface:
   - **Virtuoso**: Use the Conductor at http://localhost:8890/conductor
   - **Fuseki**: Use the UI at http://localhost:3030
   - **Stardog**: Use the Web Console at http://localhost:5820


### Navigation

The SHACL Dashboard offers two main views:

1. **Home View**
   - Overview of all validation statistics
   - Summary charts showing violation distributions
   - Key metrics on shapes, paths, and focus nodes
   - Detailed validation report table

2. **Shapes View**
   - Comprehensive analysis of individual shapes
   - Shape-specific violation statistics
   - Property shape breakdowns
   - Constraint component analysis
   - Detailed view of affected focus nodes

Use the navigation menu to switch between these views.

## Extending SHACL Dashboard

SHACL Dashboard is designed to be extensible, allowing you to add custom features and functionality to meet your specific requirements. This section provides general guidance on how to extend and customize the application.

### Extension Points

1. **Custom Visualizations**:

2. **Additional Data Analysis**:

3. **UI Customizations**:

4. **Backend Enhancements**:

5. **Integration Capabilities**:

### Extension Approach

When extending SHACL Dashboard, we recommend following these principles:

- Maintain the existing architectural patterns where possible
- Use the established component structure and naming conventions
- Document your extensions thoroughly
- Consider contributing general-purpose extensions back to the project

For more detailed guidance on specific extension scenarios, please refer to the developer documentation or contact the project maintainers.

## Project Structure

```plaintext
shacl-dashboard/
├── backend/                  # Backend server
│   ├── app.py                # Main application file
│   ├── requirements.txt       # Python dependencies
│   └── ...                    # Other backend files
├── frontend/                 # Frontend application
│   ├── src/                  # Source files
│   ├── public/                # Public assets
│   ├── package.json           # Node.js dependencies
│   └── ...                    # Other frontend files
├── docs/                     # Documentation files
│   ├── images/                # Images for documentation
│   └── ...                    # Other documentation files
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # This README file
```

## Troubleshooting

- **500 Internal Server Error**: Check the backend logs for traceback information. Common issues include database connection errors and missing environment variables.
- **CORS Errors**: Ensure the frontend and backend are running on the correct ports and that the backend allows requests from the frontend's origin.
- **Data Upload Issues**: Verify the named graphs in Virtuoso and ensure the SHACL shapes and validation reports are correctly loaded.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/YourFeature`
3. Make your changes
4. Commit your changes: `git commit -m 'Add some feature'`
5. Push to the branch: `git push origin feature/YourFeature`
6. Submit a pull request

Please ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [SHACL](https://www.w3.org/TR/shacl/) - Shapes Constraint Language
- [Virtuoso](https://virtuoso.openlinksw.com/) - RDF Database
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [Vue.js](https://vuejs.org/) - JavaScript framework
- [Chart.js](https://www.chartjs.org/) - JavaScript charting library
- [Vuetify](https://vuetifyjs.com/) - Material Design component framework for Vue.js
