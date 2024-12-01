# src/catwalk/main.py
from fastapi import FastAPI
from catwalk.api.v1 import router as api_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Catwalk",
    description="LRU-based ML Model Server",
    version="0.1.0"
)

app.include_router(api_router, prefix="/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logging.info("Catwalk starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logging.info("Catwalk shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
