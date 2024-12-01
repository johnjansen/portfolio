from pydantic import BaseModel
from typing import Dict, Any


class ModelMetadata(BaseModel):
    """Model metadata information"""
    model_id: str
    version: str
    format: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    memory_usage: str
    last_used: str
    total_requests: int
    average_latency: float
