# examples/test_inference.py
import asyncio
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_model():
    async with httpx.AsyncClient() as client:
        # Create sample input
        input_data = {
            "inputs": {
                "data": [1.0, 2.0]
            }
        }

        try:
            logger.info("Sending prediction request...")
            response = await client.post(
                "http://localhost:8000/v1/models/simple_model/predict",
                json=input_data,
                timeout=30.0
            )

            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {response.headers}")
            logger.info(f"Response Body: {response.text}")

            if response.status_code == 200:
                logger.info(f"Prediction successful: {response.json()}")
            else:
                logger.error(f"Prediction failed: {response.text}")

        except Exception as e:
            logger.error(f"Request failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_model())
