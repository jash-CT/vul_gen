from fastapi.testclient import TestClient
from placeholder_service.main import app

client = TestClient(app)

def test_health_endpoint():
    """
    Minimal health check test
    Verifies basic operational status
    """
    response = client.get("/placeholder/health")
    assert response.status_code == 200
    assert response.json() == {"status": "operational"}