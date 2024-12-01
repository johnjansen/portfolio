# src/portfolio/models/loader/__init__.py
from .base import ModelLoader
from .pytorch import PyTorchLoader
from .tensorflow import TensorFlowLoader
from typing import Optional


def get_loader(model_type: str) -> Optional[ModelLoader]:
    """Factory function to get appropriate loader"""
    loaders = {
        'pytorch': PyTorchLoader,
        'tensorflow': TensorFlowLoader,
    }

    loader_class = loaders.get(model_type.lower())
    if loader_class is None:
        return None

    return loader_class()


__all__ = ['ModelLoader', 'PyTorchLoader', 'TensorFlowLoader', 'get_loader']
