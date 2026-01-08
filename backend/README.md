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

## Environment Configuration

The backend uses a centralized configuration file (`config.py`) that defines all the environment settings:

### SPARQL Endpoint Configuration
```python
# Default SPARQL endpoint
ENDPOINT_URL = "http://localhost:8890/sparql"

# Authentication settings
AUTH_REQUIRED = False
USERNAME = ""
PASSWORD = ""

# Triple store type
TRIPLE_STORE_TYPE = "virtuoso"  # Options: "virtuoso", "fuseki", "stardog", etc.
```

### Graph URIs
```python
SHAPES_GRAPH_URI = "http://ex.org/ShapesGraph"
VALIDATION_REPORT_URI = "http://ex.org/ValidationReport"
```

### Triple Store Specific Configuration
```python
STORE_CONFIG = {
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
```

### Using Alternative SPARQL Endpoints

To use a different SPARQL endpoint:

1. Edit the `config.py` file to update the `ENDPOINT_URL` value
2. Set the appropriate `TRIPLE_STORE_TYPE` matching your endpoint type
3. Configure any authentication if required by setting `AUTH_REQUIRED`, `USERNAME`, and `PASSWORD`
4. If using store-specific operations (like data loading), ensure the corresponding settings in `STORE_CONFIG` are correctly configured

For example, to use Apache Fuseki:

```python
# SPARQL endpoint configuration
ENDPOINT_URL = "http://localhost:3030/dataset/sparql"
TRIPLE_STORE_TYPE = "fuseki"
```

To use Stardog:

```python
# SPARQL endpoint configuration
ENDPOINT_URL = "http://localhost:5820/shacldb/query"
AUTH_REQUIRED = True
USERNAME = "admin"
PASSWORD = "admin"
TRIPLE_STORE_TYPE = "stardog"
```

### Supported Triple Store Types

The configuration supports the following triple store types out of the box:
- **Virtuoso**: Full support including bulk data loading
- **Fuseki**: Query support with limited bulk loading capabilities
- **Stardog**: Query support with bulk loading capabilities

Additional triple store types can be added by extending the `STORE_CONFIG` dictionary.

## API Documentation

### Landing Endpoints

#### Load Graphs
- **URL**: `/api/landing/load-graphs`
- **Method**: `POST`
- **Description**: Load SHACL shapes and validation reports into the Virtuoso database
- **Request Body**:
  ```json
  {
    "directory": "directory/path",
    "shapes_file": "shapes.ttl",
    "report_file": "report.ttl"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**: `{ "message": "Graphs loaded successfully" }`
- **Error Response**:
  - **Code**: 400
  - **Content**: `{ "error": "directory, shapes_file, and report_file are required" }`

### Homepage Endpoints

#### Get Violation Count
- **URL**: `/api/homepage/violations/report/count`
- **Method**: `GET`
- **Query Parameters**:
  - `graph_uri` (optional): The URI of the validation report graph (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: `{ "violationCount": 42 }`

#### Get Shapes Count
- **URL**: `/api/homepage/shapes/graph/count`
- **Method**: `GET`
- **Query Parameters**:
  - `graph_uri` (optional): The URI of the shapes graph (default: "http://ex.org/ShapesGraph")
- **Success Response**:
  - **Code**: 200
  - **Content**: `{ "nodeShapes": 15 }`

#### Get Node Shapes with Violations Count
- **URL**: `/api/homepage/shapes/violations/count`
- **Method**: `GET`
- **Query Parameters**:
  - `shapes_graph_uri` (optional): The URI of the shapes graph (default: "http://ex.org/ShapesGraph")
  - `validation_report_uri` (optional): The URI of the validation report (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: `{ "nodeShapesWithViolationsCount": 10 }`

#### Get Paths Count in Graph
- **URL**: `/api/homepage/shapes/graph/paths/count`
- **Method**: `GET`
- **Query Parameters**:
  - `graph_uri` (optional): The URI of the shapes graph (default: "http://ex.org/ShapesGraph")
- **Success Response**:
  - **Code**: 200
  - **Content**: `{ "uniquePathsCount": 25 }`

#### Get Paths with Violations Count
- **URL**: `/api/homepage/validation-report/paths/violations/count`
- **Method**: `GET`
- **Query Parameters**:
  - `validation_report_uri` (optional): The URI of the validation report (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: `{ "pathsWithViolationsCount": 18 }`

#### Get Focus Nodes Count
- **URL**: `/api/homepage/validation-report/focus-nodes/count`
- **Method**: `GET`
- **Query Parameters**:
  - `validation_report_uri` (optional): The URI of the validation report (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: `{ "focusNodesCount": 30 }`

#### Get Violations by Node Shape
- **URL**: `/api/homepage/shapes/violations`
- **Method**: `GET`
- **Query Parameters**:
  - `shapes_graph_uri` (optional): The URI of the shapes graph (default: "http://ex.org/ShapesGraph")
  - `validation_report_uri` (optional): The URI of the validation report (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    { 
      "violationsPerNodeShape": [
        { "NodeShapeName": "http://ex.org/Shape1", "NumViolations": 15 },
        { "NodeShapeName": "http://ex.org/Shape2", "NumViolations": 7 }
      ]
    }
    ```

#### Get Violations by Path
- **URL**: `/api/homepage/validation-report/paths/violations`
- **Method**: `GET`
- **Query Parameters**:
  - `validation_report_uri` (optional): The URI of the validation report (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    { 
      "violationsPerPath": [
        { "PathName": "http://ex.org/property1", "NumViolations": 12 },
        { "PathName": "http://ex.org/property2", "NumViolations": 5 }
      ]
    }
    ```

#### Get Violations by Focus Node
- **URL**: `/api/homepage/validation-report/focus-nodes/violations`
- **Method**: `GET`
- **Query Parameters**:
  - `validation_report_uri` (optional): The URI of the validation report (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    { 
      "violationsPerFocusNode": [
        { "FocusNodeName": "http://ex.org/entity1", "NumViolations": 8 },
        { "FocusNodeName": "http://ex.org/entity2", "NumViolations": 3 }
      ]
    }
    ```

#### Get Distribution of Violations per Shape
- **URL**: `/api/homepage/violations/distribution/shape`
- **Method**: `GET`
- **Query Parameters**:
  - `shapes_graph_uri` (optional): The URI of the shapes graph (default: "http://ex.org/ShapesGraph")
  - `validation_report_uri` (optional): The URI of the validation report (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    {
      "labels": ["0-10", "11-20", "21-30"],
      "datasets": [
        {
          "label": "Frequency",
          "data": [5, 3, 2]
        }
      ]
    }
    ```

#### Get Validation Details Report
- **URL**: `/api/homepage/validation-details`
- **Method**: `GET`
- **Query Parameters**:
  - `validation_report_uri` (optional): The URI of the validation report (default: "http://ex.org/ValidationReport")
  - `shapes_graph_uri` (optional): The URI of the shapes graph (default: "http://ex.org/ShapesGraph")
  - `limit` (optional): Maximum number of violations to return (default: 10)
  - `offset` (optional): Offset for pagination (default: 0)
- **Success Response**:
  - **Code**: 200
  - **Content**: Detailed validation report with prefixes and violations

### Shapes Overview Endpoints

#### Get All Shapes Names
- **URL**: `/api/shapes/names`
- **Method**: `GET`
- **Query Parameters**:
  - `graph_uri` (optional): The URI of the validation report graph (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    {
      "shapes": [
        "http://ex.org/PersonShape",
        "http://ex.org/AddressShape"
      ]
    }
    ```

#### Get All Focus Node Names
- **URL**: `/api/focus-nodes/names`
- **Method**: `GET`
- **Query Parameters**:
  - `graph_uri` (optional): The URI of the validation report graph (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    {
      "focusNodes": [
        "http://ex.org/person1",
        "http://ex.org/person2"
      ]
    }
    ```

#### Get All Property Path Names
- **URL**: `/api/property-paths/names`
- **Method**: `GET`
- **Query Parameters**:
  - `graph_uri` (optional): The URI of the validation report graph (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    {
      "propertyPaths": [
        "http://ex.org/name",
        "http://ex.org/age"
      ]
    }
    ```

#### Get All Constraint Component Names
- **URL**: `/api/constraint-components/names`
- **Method**: `GET`
- **Query Parameters**:
  - `graph_uri` (optional): The URI of the validation report graph (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    {
      "constraintComponents": [
        "http://www.w3.org/ns/shacl#MinCountConstraintComponent",
        "http://www.w3.org/ns/shacl#DatatypeConstraintComponent"
      ]
    }
    ```

#### Get Violations for a Shape
- **URL**: `/api/violations/shape`
- **Method**: `GET`
- **Query Parameters**:
  - `shape_name` (required): The URI of the shape to query
  - `graph_uri` (optional): The URI of the validation report graph (default: "http://ex.org/ValidationReport")
- **Success Response**:
  - **Code**: 200
  - **Content**: Array of violation objects

#### Get Property Shapes to Node Shapes Mapping
- **URL**: `/api/property-to-node/map`
- **Method**: `GET`
- **Query Parameters**:
  - `validation_report_uri` (optional): The URI of the validation report (default: "http://ex.org/ValidationReport")
  - `shapes_graph_uri` (optional): The URI of the shapes graph (default: "http://ex.org/ShapesGraph")
- **Success Response**:
  - **Code**: 200
  - **Content**: Mapping between property shapes and node shapes

#### Get Shape Details
- **URL**: `/api/shapes/graph/details`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "node_shape_names": ["http://ex.org/PersonShape", "http://ex.org/AddressShape"]
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**: Detailed information about the requested node shapes

#### Get Maximum Number of Violations
- **URL**: `/api/violations/max`
- **Method**: `GET`
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    {
      "nodeShape": "http://ex.org/MostViolatedShape",
      "violationCount": 42
    }
    ```

#### Get Average Number of Violations
- **URL**: `/api/violations/average`
- **Method**: `GET`
- **Success Response**:
  - **Code**: 200
  - **Content**: `{ "averageViolations": 7.5 }`

#### Get Violations for a Node Shape
- **URL**: `/api/violations/node-shape/count`
- **Method**: `GET`
- **Query Parameters**:
  - `nodeshape_name` (required): The URI of the node shape to query
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    {
      "nodeShape": "http://ex.org/PersonShape",
      "violationCount": 15
    }
    ```

#### Get Property Shapes for a Node Shape
- **URL**: `/api/node-shape/property-shapes`
- **Method**: `GET`
- **Query Parameters**:
  - `node_shape` (required): The URI of the node shape to query
  - `limit` (optional): Maximum number of property shapes to return
  - `offset` (optional): Offset for pagination
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    {
      "nodeShape": "http://ex.org/PersonShape",
      "propertyShapes": [
        {
          "PropertyShapeName": "http://ex.org/PersonNamePropertyShape",
          "NumViolations": 5,
          "NumConstraints": 2,
          "MostViolatedConstraint": "http://www.w3.org/ns/shacl#MinCountConstraintComponent"
        }
      ]
    }
    ```

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