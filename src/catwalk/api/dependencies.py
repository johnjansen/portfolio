# src/catwalk/api/dependencies.py
from typing import Annotated
from fastapi import Depends
from catwalk.core.manager import ModelManager
from catwalk.utils.metrics import MetricsCollector
import os

# Singleton instances
_model_manager: ModelManager = None
_metrics_collector: MetricsCollector = None

def get_config_path() -> str:
    """Get configuration path from environment or default"""
    return os.getenv('CATWALK_CONFIG_PATH', 'config/development/config.yaml')

def get_model_manager() -> ModelManager:
    """Dependency provider for ModelManager"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager(get_config_path())
    return _model_manager

def get_metrics_collector() -> MetricsCollector:
    """Dependency provider for MetricsCollector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

# Type aliases for dependency injection
ModelManagerDep = Annotated[ModelManager, Depends(get_model_manager)]
MetricsCollectorDep = Annotated[MetricsCollector, Depends(get_metrics_collector)]
