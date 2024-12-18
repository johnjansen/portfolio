# src/portfolio/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from portfolio.api.v1 import router as api_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logging.info("Portfolio starting up...")
    yield
    # Shutdown
    logging.info("Portfolio shutting down...")

app = FastAPI(
    title="Portfolio",
    description="LRU-based ML Model Server",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
