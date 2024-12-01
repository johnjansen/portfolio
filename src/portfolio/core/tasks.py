# src/portfolio/core/tasks.py
import asyncio


class BackgroundModelManager:
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            await self._cleanup_unused_models()
            await asyncio.sleep(60)

    async def _cleanup_unused_models(self):
        """Remove models that haven't been used recently"""
        # Implementation here
