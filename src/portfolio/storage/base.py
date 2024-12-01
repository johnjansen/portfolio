# src/portfolio/storage/base.py
from abc import ABC, abstractmethod
from typing import BinaryIO, AsyncIterator


class ModelStorage(ABC):
    """Abstract interface for model storage backends"""

    @abstractmethod
    async def get_model(self, model_id: str) -> AsyncIterator[bytes]:
        """Retrieve model data"""
        pass

    @abstractmethod
    async def store_model(self, model_id: str, data: BinaryIO) -> None:
        """Store model data"""
        pass

    @abstractmethod
    async def delete_model(self, model_id: str) -> None:
        """Delete a model"""
        pass
