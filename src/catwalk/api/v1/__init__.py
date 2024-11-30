# catwalk/src/catwalk/api/v1/__init__.py

from fastapi import APIRouter
from .routes import router as model_router

router = APIRouter()
router.include_router(model_router, tags=["models"])
