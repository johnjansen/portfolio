# tests/unit/test_system_status.py
import pytest
from fastapi.testclient import TestClient
from src.portfolio.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_system_status_endpoint(client):
    """Test the /models/status endpoint returns correct data structure"""
    response = client.get("/v1/models/status")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["active_models"], int)
    assert isinstance(data["total_memory_usage"], str)
    assert isinstance(data["cache_utilization"], float)
    assert isinstance(data["healthy"], bool)
    assert isinstance(data["uptime"], str)

    # Verify memory usage format
    assert "MB" in data["total_memory_usage"]

    # Verify cache utilization is between 0 and 1
    assert 0 <= data["cache_utilization"] <= 1

    # Verify uptime format
    assert "s" in data["uptime"]


def test_system_status_with_loaded_models(client):
    """Test status endpoint with actual loaded models"""
    # First load a model
    input_data = {"inputs": {"data": [1.0, 2.0]}}
    client.post("/v1/models/simple_model/predict", json=input_data)

    # Then check status
    response = client.get("/v1/models/status")
    assert response.status_code == 200

    data = response.json()
    assert data["active_models"] > 0
    assert float(data["total_memory_usage"].replace("MB", "")) > 0
