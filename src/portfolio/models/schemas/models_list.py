from dataclasses import dataclass
from typing import List

from .model_summary import ModelSummary


@dataclass
class ModelsList:
    """Collection of model summaries with count information"""
    models: List[ModelSummary]
    total_count: int
    loaded_count: int
