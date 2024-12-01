from pydantic import BaseModel, Field
from typing import Dict, Any


class PredictionResponse(BaseModel):
    """Standard prediction response structure"""
    model_id: str = Field(..., description="ID of the model used for inference")
    outputs: Dict[str, Any] = Field(..., description="Model predictions")
    metadata: Dict[str, Any] = Field(default={}, description="Additional prediction metadata")
