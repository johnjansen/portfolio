# src/catwalk/api/v1/routes.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from catwalk.api.dependencies import ModelManagerDep, MetricsCollectorDep
import time
import logging

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class PredictionRequest(BaseModel):
    """Input data structure for model predictions"""
    inputs: Dict[str, Any] = Field(..., description="Model input data")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Optional inference parameters")

    class Config:
        schema_extra = {
            "example": {
                "inputs": {"text": "Sample input text"},
                "parameters": {"temperature": 0.7}
            }
        }


class PredictionResponse(BaseModel):
    """Standard prediction response structure"""
    model_id: str = Field(..., description="ID of the model used for inference")
    outputs: Dict[str, Any] = Field(..., description="Model predictions")
    metadata: Dict[str, Any] = Field(default={}, description="Additional prediction metadata")


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


class SystemStatus(BaseModel):
    """System-wide status information"""
    active_models: int
    total_memory_usage: str
    cache_utilization: float
    healthy: bool
    uptime: str


class ModelSummary(BaseModel):
    """Summary information for a model"""
    model_id: str = Field(..., description="Unique identifier for the model")
    status: str = Field(..., description="Current model status (loaded/unloaded)")
    format: str = Field(..., description="Model format (pytorch/tensorflow/etc)")
    memory_usage: str = Field(..., description="Current memory usage")
    last_used: str = Field(..., description="Timestamp of last usage")
    is_loaded: bool = Field(..., description="Whether model is currently loaded")


class ModelsList(BaseModel):
    """List of models with their statuses"""
    models: list[ModelSummary] = Field(..., description="List of model summaries")
    total_count: int = Field(..., description="Total number of models")
    loaded_count: int = Field(..., description="Number of currently loaded models")


@router.get("/models", response_model=ModelsList)
async def list_models() -> ModelsList:
    """
    List all available models and their current status.

    Returns:
        ModelsList containing summaries of all registered models

    Raises:
        HTTPException: If unable to retrieve model list
    """
    try:
        # TODO: Implement actual model listing logic
        return ModelsList(
            models=[
                ModelSummary(
                    model_id="example-model",
                    status="loaded",
                    format="pytorch",
                    memory_usage="0MB",
                    last_used="never",
                    is_loaded=True
                )
            ],
            total_count=1,
            loaded_count=1
        )
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models list")


@router.post("/models/{model_id}/predict", response_model=PredictionResponse)
async def predict(
    model_id: str,
    request: PredictionRequest,
    model_manager: ModelManagerDep,
    metrics: MetricsCollectorDep,
    background_tasks: BackgroundTasks
) -> PredictionResponse:
    """Perform model inference on the provided input data."""
    try:
        logger.info(f"Received prediction request for model: {model_id}")
        logger.debug(f"Input data: {request.inputs}")

        start_time = time.time()

        # Get model from manager (handles loading if needed)
        model = await model_manager.get_model(model_id)
        if model is None:
            raise HTTPException(
                status_code=404,
                detail=f"Model {model_id} not found or failed to load"
            )

        # Perform inference
        outputs = await model_manager.predict(
            model_id,
            request.inputs,
            request.parameters or {}
        )

        logger.info(f"Inference completed for model {model_id}")
        logger.debug(f"Outputs: {outputs}")

        # Record metrics
        duration = time.time() - start_time
        background_tasks.add_task(metrics.record_inference, model_id, duration)

        return PredictionResponse(
            model_id=model_id,
            outputs=outputs,
            metadata={
                "duration_ms": round(duration * 1000, 2),
                "model_version": getattr(model, 'version', 'unknown')
            }
        )

    except Exception as e:
        logger.error(f"Prediction failed for model {model_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}/metadata", response_model=ModelMetadata)
async def get_model_metadata(
    model_id: str,
    model_manager: ModelManagerDep,
    metrics: MetricsCollectorDep
) -> ModelMetadata:
    """Retrieve metadata for a specific model."""
    try:
        model_info = await model_manager.get_model_info(model_id)
        if model_info is None:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

        return ModelMetadata(
            model_id=model_id,
            version=model_info.version,
            format=model_info.format,
            input_schema=model_info.input_schema,
            output_schema=model_info.output_schema,
            memory_usage=f"{model_info.memory_usage / (1024*1024):.2f}MB",
            last_used=model_info.last_used.isoformat() if model_info.last_used else "never",
            total_requests=metrics.get_request_count(),
            average_latency=metrics.get_inference_time_avg(model_id)
        )
    except Exception as e:
        logger.error(f"Failed to retrieve metadata for model {model_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/status", response_model=SystemStatus)
async def get_system_status(
    model_manager: ModelManagerDep,
    metrics: MetricsCollectorDep
) -> SystemStatus:
    """Get system-wide status information."""
    try:
        system_metrics = metrics.get_system_metrics()
        cache_stats = model_manager.cache.stats()

        return SystemStatus(
            active_models=len(model_manager.models),
            total_memory_usage=f"{system_metrics['memory_usage'] / (1024*1024):.2f}MB",
            cache_utilization=cache_stats['utilization'],
            healthy=True,
            uptime=f"{system_metrics['uptime']:.1f}s"
        )
    except Exception as e:
        logger.error(f"Failed to retrieve system status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.

    Returns:
        Dictionary with status information
    """
    return {"status": "healthy"}
