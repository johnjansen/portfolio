# src/portfolio/models/loader/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class ModelLoader(ABC):
    @abstractmethod
    async def load(self, path: str) -> Any:
        """Load a model from the given path"""
        pass

    @abstractmethod
    def get_memory_usage(self, model: Any) -> int:
        """Get model's memory usage in bytes"""
        pass

    @abstractmethod
    async def predict(self, model: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run model prediction"""
        pass
