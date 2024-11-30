# src/catwalk/main.py
from fastapi import FastAPI
from catwalk.api.v1 import router as api_router

app = FastAPI(title="Catwalk", description="LRU-based ML Model Server")

app.include_router(api_router, prefix="/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
