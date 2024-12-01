from datetime import datetime
from typing import NamedTuple, Dict, Optional, Any


class ModelInfo(NamedTuple):
    """Model metadata container"""
    version: str
    format: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    memory_usage: int
    last_used: Optional[datetime]
