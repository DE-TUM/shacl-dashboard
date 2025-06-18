# SHACL Dashboard Backend

This is the backend server for the SHACL Dashboard, built with Flask. It provides a RESTful API for loading and querying SHACL validation reports and shapes graphs stored in a Virtuoso database.

## Features

- RESTful API for SHACL validation results analysis
- Integration with Virtuoso RDF database
- Support for loading RDF files into Virtuoso
- Comprehensive query capabilities for SHACL validation reports
- Detailed statistics and metrics for violations

## Project Structure

```
backend/
  ├── app.py                # Main Flask application entry point
  ├── requirements.txt      # Python dependencies
  ├── evaluation/           # Evaluation scripts and results
  │   └── ...               # Various evaluation output files
  ├── functions/            # Core functionality and services
  │   ├── __init__.py       # Function exports
  │   ├── homepage_service.py         # Main dashboard data services
  │   ├── landing_service.py          # Data loading services
  │   ├── shapes_overview_service.py  # Shape analysis services
  │   └── virtuoso_service.py         # Database connectivity services
  └── routes/               # API route definitions
      ├── __init__.py       # Blueprint registration
      ├── homepage_routes.py          # Main dashboard endpoints
      ├── landing_routes.py           # File loading endpoints
      ├── shapes_overview_routes.py   # Shape analysis endpoints
      └── shape_view_routes.py        # Shape detail endpoints
```

## API Endpoints

### Landing

- `POST /load-graphs`: Load shapes and validation report into Virtuoso

### Homepage (Dashboard Overview)

- `GET /homepage/violations/report/count`: Get total violation count
- `GET /homepage/shapes/graph/count`: Get shapes count in graph
- `GET /homepage/shapes/graph/violations/count`: Get count of shapes with violations
- `GET /homepage/shapes/graph/paths/count`: Get count of property paths in shapes graph
- `GET /homepage/validation-report/paths/violations/count`: Get count of paths with violations
- `GET /homepage/validation-report/focus-nodes/count`: Get count of focus nodes in validation report
- `GET /homepage/shapes/violations`: Get violations per node shape
- `GET /homepage/validation-report/paths/violations`: Get violations per property path
- `GET /homepage/validation-report/focus-nodes/violations`: Get violations per focus node
- `GET /homepage/violations/distribution/shape`: Get distribution of violations per shape
- `GET /homepage/violations/distribution/path`: Get distribution of violations per path
- `GET /homepage/violations/distribution/focus-node`: Get distribution of violations per focus node
- `GET /homepage/validation-details`: Get detailed validation report

### Shapes Overview

- `GET /shapes/names`: Get all shape names
- `GET /focus-nodes/names`: Get all focus node names
- `GET /property-paths/names`: Get all property path names
- `GET /constraint-components/names`: Get all constraint component names
- `GET /violations/shape`: Get violations for a specific shape
- `GET /shapes/graph/count`: Get number of shapes in shapes graph
- `GET /property-to-node/map`: Get mapping of property shapes to node shapes
- `POST /shapes/graph/details`: Get details for specific node shapes

## Getting Started

### Prerequisites

- Python 3.8+
- Virtuoso RDF Database
- ISQL CLI tool (for Virtuoso interaction)

### Installation

1. Install Python dependencies:

```sh
pip install -r requirements.txt
```

2. Ensure Virtuoso is running (default configuration expects it at localhost:8890)

3. Run the backend server:

```sh
python app.py
```

The backend will be accessible at [http://localhost:80](http://localhost:80).

## Environment Configuration

The backend uses the following configuration:

- SPARQL Endpoint: `http://localhost:8890/sparql`
- Shapes Graph URI: `http://ex.org/ShapesGraph`
- Validation Report URI: `http://ex.org/ValidationReport`

## Docker Support

The backend can also be run with Docker, as defined in the root [Dockerfile](../Dockerfile).