# tests/integration/test_system_monitoring.py
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from portfolio.api.v1 import router as api_router
from portfolio.api.dependencies import reset_model_manager
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def app():
    """Create a fresh FastAPI application instance for each test"""
    # Reset global state
    reset_model_manager()

    # Create new application
    app = FastAPI(title="Portfolio Test")
    app.include_router(api_router, prefix="/v1")

    return app

@pytest.fixture
def client(app):
    """Create a fresh test client for each test"""
    return TestClient(app)

@pytest.mark.asyncio
async def test_system_monitoring_flow(client):
    """Test the complete system monitoring flow"""
    # 1. Check initial status
    initial_status = client.get("/v1/models/status")
    assert initial_status.status_code == 200
    initial_data = initial_status.json()
    logger.info(f"Initial status: {initial_data}")

    # Verify we start with no active models
    assert initial_data["active_models"] == 0, "Expected no active models at start"

    # 2. Load a model through prediction
    prediction_data = {
        "inputs": {
            "data": [1.0, 2.0]
        }
    }
    prediction_response = client.post("/v1/models/simple_model/predict", json=prediction_data)
    assert prediction_response.status_code == 200, f"Prediction failed: {prediction_response.text}"
    logger.info(f"Prediction response: {prediction_response.json()}")

    # 3. Check updated status
    updated_status = client.get("/v1/models/status")
    assert updated_status.status_code == 200
    updated_data = updated_status.json()
    logger.info(f"Updated status: {updated_data}")

    # 4. Verify changes
    assert updated_data["active_models"] == 1, (
        f"Expected exactly one active model, got: {updated_data['active_models']}"
    )

    # Additional assertions
    assert float(updated_data["total_memory_usage"].replace("MB", "")) > \
           float(initial_data["total_memory_usage"].replace("MB", "")), \
           "Memory usage did not increase after loading model"

    assert updated_data["cache_utilization"] > initial_data["cache_utilization"], \
           "Cache utilization did not increase after loading model"
