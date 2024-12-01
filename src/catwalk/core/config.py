# src/catwalk/utils/config.py
from pathlib import Path
import yaml
from typing import Dict, Any
from pydantic import BaseModel

class ModelConfig(BaseModel):
    path: str
    type: str
    memory_estimate: str
    preload: bool = False
    version: str = "1.0.0"

class CacheConfig(BaseModel):
    max_memory: str
    soft_limit: str
    ttl: int = 3600

class Config(BaseModel):
    models: Dict[str, ModelConfig]
    cache: CacheConfig

def load_config(path: str) -> Config:
    """Load and validate configuration"""
    with open(path) as f:
        raw_config = yaml.safe_load(f)
    return Config(**raw_config)
