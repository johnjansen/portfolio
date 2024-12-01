from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Optional, Any


class PredictionRequest(BaseModel):
    """Input data structure for model predictions"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "inputs": {"text": "Sample input text"},
                "parameters": {"temperature": 0.7}
            }
        }
    )

    inputs: Dict[str, Any] = Field(..., description="Model input data")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Optional inference parameters")
