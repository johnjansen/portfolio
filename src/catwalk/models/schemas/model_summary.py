from dataclasses import dataclass


@dataclass
class ModelSummary:
    """Represents summary information for a single model"""
    model_id: str
    status: str  # "loaded", "unloaded", "error"
    format: str  # "pytorch", "tensorflow", etc
    memory_usage: str
    last_used: str
    is_loaded: bool
