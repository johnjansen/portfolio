# src/portfolio/api/dependencies.py
from typing import Annotated, Optional
from portfolio.core.manager import ModelManager
from portfolio.utils.metrics import MetricsCollector
import os
import logging

from fastapi import Depends

logger = logging.getLogger(__name__)


# Singleton instances
_model_manager: Optional[ModelManager] = None
_metrics_collector: Optional[MetricsCollector] = None


def get_config_path() -> str:
    """Get configuration path from environment or default"""
    return os.getenv('PORTFOLIO_CONFIG_PATH', 'config/development/config.yaml')


def reset_model_manager():
    """Reset the global model manager instance"""
    global _model_manager
    if _model_manager is not None:
        # Clean up existing manager
        for model_id in list(_model_manager._active_models):
            _model_manager.remove_model(model_id)
        _model_manager.cache.clear()
    _model_manager = None
    logger.info("Reset global ModelManager instance")

def get_model_manager() -> ModelManager:
    """Dependency provider for ModelManager"""
    global _model_manager
    if _model_manager is None:
        config_path = os.getenv('PORTFOLIO_CONFIG_PATH', 'config/development/config.yaml')
        logger.info(f"Creating new ModelManager with config: {config_path}")
        _model_manager = ModelManager(config_path)
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
