import os
from typing import Any, Dict
import logging
import torch
from .base import ModelLoader

logger = logging.getLogger(__name__)


class PyTorchLoader(ModelLoader):
    def __init__(self):
        self.torch = torch

    async def load(self, path: str) -> Any:
        try:
            # Log absolute path for debugging
            abs_path = os.path.abspath(path)
            logger.info(f"Loading PyTorch model from: {abs_path}")

            if not os.path.exists(abs_path):
                logger.error(f"Model file not found at: {abs_path}")
                return None

            model = self.torch.jit.load(abs_path)
            model.eval()  # Set to evaluation mode
            logger.info(f"Successfully loaded PyTorch model from: {abs_path}")
            return model

        except Exception as e:
            logger.error(f"Failed to load PyTorch model from {path}: {str(e)}")
            return None

    def get_memory_usage(self, model: Any) -> int:
        try:
            return sum(p.numel() * p.element_size() for p in model.parameters())
        except Exception as e:
            logger.error(f"Failed to calculate model memory usage: {str(e)}")
            return 0

    async def predict(self, model: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Convert input data to tensor
            input_data = inputs.get('data', [])
            input_tensor = self.torch.tensor(input_data, dtype=self.torch.float32)

            # Run inference
            with self.torch.no_grad():
                output = model(input_tensor)

            # Convert output to Python types for JSON serialization
            return {"output": output.tolist()}
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
