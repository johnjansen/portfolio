# src/catwalk/core/manager.py
from typing import Optional, Dict, Any, NamedTuple
from datetime import datetime
import os
import re
import yaml
import logging
from .cache import LRUCache  # Make sure this import is here
from ..models.loader import PyTorchLoader, TensorFlowLoader

logger = logging.getLogger(__name__)


class ModelInfo(NamedTuple):
    """Model metadata container"""
    version: str
    format: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    memory_usage: int
    last_used: Optional[datetime]


class ModelManager:
    def __init__(self, config_path: str):
        """Initialize the model manager with configuration."""
        logger.info(f"Initializing ModelManager with config from: {config_path}")

        # Store the config directory for relative paths
        self.config_dir = os.path.dirname(os.path.abspath(config_path))
        self.config = self._load_config(config_path)

        # Initialize cache
        max_memory = self.config['cache']['max_memory']
        soft_limit = self.config['cache']['soft_limit']

        logger.debug(f"Parsing max memory: {max_memory}")
        max_size_bytes = self._parse_size(max_memory)

        logger.debug(f"Parsing soft limit: {soft_limit}")
        soft_limit_bytes = self._parse_size(soft_limit)

        logger.info(
            f"Initializing cache with max_size={max_size_bytes:,} bytes, soft_limit={soft_limit_bytes:,} bytes"
        )

        # Create the cache instance
        self.cache: LRUCache = LRUCache(
            max_size_bytes=max_size_bytes,
            soft_limit_bytes=soft_limit_bytes
        )

        # Initialize model loaders
        self.loaders = {
            'pytorch': PyTorchLoader(),
            'tensorflow': TensorFlowLoader()
        }

        # Initialize model storage
        self.models: Dict[str, Any] = {}
        self.model_info: Dict[str, ModelInfo] = {}

        logger.info(f"Initialized loaders for: {', '.join(self.loaders.keys())}")

    def _resolve_path(self, path: str) -> str:
        """Resolve a path relative to the config file location"""
        if os.path.isabs(path):
            return path
        return os.path.abspath(os.path.join(self.config_dir, '..', '..', path))

    async def _load_model(self, model_id: str) -> Optional[Any]:
        """Load a model from storage."""
        if model_id not in self.config['models']:
            logger.warning(f"Model {model_id} not found in configuration")
            return None

        try:
            model_config = self.config['models'][model_id]
            model_type = model_config['type'].lower()

            # Resolve the model path
            model_path = self._resolve_path(model_config['path'])
            logger.info(f"Resolved model path: {model_path}")

            loader = self.loaders.get(model_type)
            if loader is None:
                logger.error(f"No loader available for model type: {model_type}")
                return None

            logger.info(f"Loading model {model_id} using {model_type} loader")
            model = await loader.load(model_path)

            if model is None:
                logger.error(f"Failed to load model {model_id}")
                return None

            memory_usage = loader.get_memory_usage(model)
            logger.info(f"Model {model_id} loaded, using {memory_usage:,} bytes")

            # Store in cache
            self.cache.put(model_id, model, memory_usage)

            return model

        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {str(e)}")
            return None

    async def get_model(self, model_id: str) -> Optional[Any]:
        """Get a model, loading it if necessary."""
        logger.debug(f"Getting model: {model_id}")
        model = self.cache.get(model_id)
        if model is None:
            logger.info(f"Model {model_id} not in cache, loading...")
            model = await self._load_model(model_id)
        return model

    async def predict(
        self,
        model_id: str,
        inputs: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform model inference."""
        model = await self.get_model(model_id)
        if model is None:
            raise ValueError(f"Model {model_id} not found")

        model_config = self.config['models'][model_id]
        model_type = model_config['type'].lower()
        loader = self.loaders.get(model_type)

        if loader is None:
            raise ValueError(f"No loader available for model type: {model_type}")

        logger.debug(f"Running prediction for model {model_id}")
        return await loader.predict(model, inputs)

    def _parse_size(self, size_str: str) -> int:
        """Convert size string (e.g., '1GB') to bytes."""
        if not isinstance(size_str, str):
            raise ValueError(f"Size must be a string, got {type(size_str)}")

        size_str = str(size_str).strip()

        match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B)$', size_str.upper())
        if not match:
            raise ValueError(f"Invalid size format: {size_str}. Expected format: '1GB', '100MB', etc.")

        number, unit = match.groups()
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4
        }

        try:
            return int(float(number) * multipliers[unit])
        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid size format: {size_str}") from e

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        logger.info(f"Loading config from: {config_path}")
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.debug(f"Loaded config: {config}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {str(e)}")
            raise

    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """
        Retrieve metadata information for a specific model.

        Args:
            model_id (str): The unique identifier for the model

        Returns:
            Optional[ModelInfo]: Model metadata if found, None otherwise

        Raises:
            ValueError: If the model_id is invalid or not found in configuration
        """
        logger.debug(f"Getting model info for: {model_id}")

        # Check if model exists in configuration
        if model_id not in self.config['models']:
            logger.warning(f"Model {model_id} not found in configuration")
            return None

        model_config = self.config['models'][model_id]

        try:
            # Get the model to ensure memory usage is accurate
            model = await self.get_model(model_id)
            if model is None:
                return None

            # Get the appropriate loader
            model_type = model_config['type'].lower()
            loader = self.loaders.get(model_type)

            if loader is None:
                logger.error(f"No loader available for model type: {model_type}")
                return None

            # Gather model information
            return ModelInfo(
                version=model_config.get('version', '1.0.0'),
                format=model_type,
                input_schema=model_config.get('input_schema', {}),
                output_schema=model_config.get('output_schema', {}),
                memory_usage=loader.get_memory_usage(model),
                last_used=self.cache.get_last_access_time(model_id)
            )

        except Exception as e:
            logger.error(f"Failed to get model info for {model_id}: {str(e)}")
            return None
