# src/portfolio/models/loader/tensorflow.py
from typing import Any, Dict
import logging
from .base import ModelLoader

logger = logging.getLogger(__name__)


class TensorFlowLoader(ModelLoader):
    def __init__(self):
        try:
            import tensorflow as tf
            self.tf = tf
        except ImportError:
            logger.warning("TensorFlow not installed")
            self.tf = None

    async def load(self, path: str) -> Any:
        if self.tf is None:
            return None
            try:
                import tensorflow.saved_model as saved_model
                return saved_model.load(path)
            except ImportError:
                logger.error("Could not import tensorflow.saved_model")
                return None

    def get_memory_usage(self, model: Any) -> int:
        if self.tf is None:
            return 0
        return sum(w.numpy().nbytes for w in model.weights)

    async def predict(self, model: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if self.tf is None:
            raise RuntimeError("TensorFlow not installed")
        raise NotImplementedError("TensorFlow prediction not implemented")
