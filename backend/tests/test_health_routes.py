"""
Basic integration tests for health routes.
"""
import pytest
from flask import Flask
from routes.health_routes import health_bp


@pytest.fixture
def app():
    """Create test Flask application with health routes"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(health_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_basic_health_check(self, client):
        """Should return 200 for basic health check"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'healthy'
    
    def test_readiness_probe(self, client):
        """Should have readiness probe endpoint"""
        response = client.get('/health/ready')
        # May return 200 or 503 depending on SPARQL endpoint availability
        assert response.status_code in [200, 503]
    
    def test_liveness_probe(self, client):
        """Should return 200 for liveness probe"""
        response = client.get('/health/live')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'alive'
