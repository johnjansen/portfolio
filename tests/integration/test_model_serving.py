# tests/integration/test_model_serving.py
import pytest
from httpx import AsyncClient
from catwalk.main import app

@pytest.mark.asyncio
async def test_model_inference():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/models/test-model/predict",
            json={"inputs": {"text": "test input"}}
        )
        assert response.status_code == 200
        assert "outputs" in response.json()
