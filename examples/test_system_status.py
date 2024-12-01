import asyncio
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_system_status():
    async with httpx.AsyncClient() as client:
        try:
            logger.info("Checking system status...")
            response = await client.get(
                "http://localhost:8000/v1/models/status",
                timeout=30.0
            )

            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {response.headers}")
            logger.info(f"Response Body: {response.text}")

            if response.status_code == 200:
                status = response.json()
                logger.info("\nSystem Status:")
                logger.info(f"Active Models: {status['active_models']}")
                logger.info(f"Memory Usage: {status['total_memory_usage']}")
                logger.info(f"Cache Utilization: {status['cache_utilization']:.2%}")
                logger.info(f"Healthy: {status['healthy']}")
                logger.info(f"Uptime: {status['uptime']}")
            else:
                logger.error(f"Status check failed: {response.text}")

        except Exception as e:
            logger.error(f"Request failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_system_status())
