# tests/integration/test_model_serving.py
import pytest
from fastapi.testclient import TestClient
from catwalk.main import app
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_model_inference(client):
    """Test model inference with the simple_model"""
    # Prepare test input matching our simple model's expected format
    input_data = {
        "inputs": {
            "data": [1.0, 2.0]  # Simple model expects 2 input values
        }
    }

    logger.info("Sending prediction request to simple_model")
    response = client.post(
        "/v1/models/simple_model/predict",
        json=input_data
    )

    # Log response details for debugging
    logger.info(f"Response status: {response.status_code}")
    if response.status_code != 200:
        logger.error(f"Response body: {response.text}")

    assert response.status_code == 200

    response_data = response.json()
    assert "outputs" in response_data
    assert "metadata" in response_data
    assert "duration_ms" in response_data["metadata"]

    # Verify output structure
    outputs = response_data["outputs"]
    assert "output" in outputs
    assert isinstance(outputs["output"], list)  # Should be a single float in a list
