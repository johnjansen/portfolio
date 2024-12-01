# src/catwalk/storage/filesystem.py
from pathlib import Path
from typing import AsyncIterator, BinaryIO
import aiofiles
from .base import ModelStorage


class FileSystemStorage(ModelStorage):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    async def get_model(self, model_id: str) -> AsyncIterator[bytes]:
        async def stream() -> AsyncIterator[bytes]:
            path = self.base_path / f"{model_id}.pt"
            async with aiofiles.open(path, 'rb') as f:
                while chunk := await f.read(8192):
                    yield chunk
        return stream()

    async def store_model(self, model_id: str, data: BinaryIO) -> None:
        path = self.base_path / f"{model_id}.pt"
        async with aiofiles.open(path, 'wb') as f:
            while chunk := data.read(8192):
                await f.write(chunk)
