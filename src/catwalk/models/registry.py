# src/catwalk/models/registry.py
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Manages model registration and status tracking"""

    def __init__(self):
        self._models: Dict[str, dict] = {}

    def register_model(self, model_id: str, format: str):
        """Register a new model with the registry"""
        self._models[model_id] = {
            "format": format,
            "loaded": False,
            "last_used": None,
            "memory_usage": "0MB"
        }

    def get_all_models(self) -> List[dict]:
        """Retrieve all registered models with their current status"""
        return [
            {"model_id": k, **v}
            for k, v in self._models.items()
        ]


# Global instance
model_registry = ModelRegistry()
