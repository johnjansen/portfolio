# src/portfolio/api/v1/routes.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from portfolio.api.dependencies import ModelManagerDep, MetricsCollectorDep
import time
import logging
from datetime import datetime
import humanize  # Add this to requirements.txt if not present


from typing import Dict, List
from pydantic import Field


# request and response schemas
from portfolio.models.schemas.model_summary import ModelSummary
from portfolio.models.schemas.models_list import ModelsList
from portfolio.models.schemas.prediction_response import PredictionResponse
from portfolio.models.schemas.model_metadata import ModelMetadata
from portfolio.models.schemas.system_status import SystemStatus
from portfolio.models.schemas.prediction_request import PredictionRequest


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/models", response_model=ModelsList)
async def list_models(
    model_manager: ModelManagerDep,
    metrics: MetricsCollectorDep
) -> ModelsList:
    """
    List all available models and their current status.

    Returns:
        ModelsList containing summaries of all registered models
    """
    try:
        # Get models from configuration
        models_config = model_manager.config.get('models', {})
        model_summaries: List[ModelSummary] = []
        loaded_count = 0

        for model_id, config in models_config.items():
            # Check if model is currently in cache
            is_loaded = model_manager.cache.get(model_id) is not None
            if is_loaded:
                loaded_count += 1
                status = "loaded"
            else:
                status = "unloaded"

            # Get last access time
            last_access = model_manager.cache.get_last_access_time(model_id)
            if last_access:
                last_used = humanize.naturaltime(datetime.now() - last_access)
            else:
                last_used = "never"

            # Get memory usage
            if is_loaded:
                model = await model_manager.get_model(model_id)
                if model:
                    loader = model_manager.loaders.get(config['type'].lower())
                    if loader is not None:
                        memory_bytes = loader.get_memory_usage(model)
                        memory_usage = humanize.naturalsize(memory_bytes)
                    else:
                        memory_usage = "unknown"
                else:
                    memory_usage = "unknown"
            else:
                memory_usage = "0 B"

            model_summaries.append(ModelSummary(
                model_id=model_id,
                status=status,
                format=config['type'],
                memory_usage=memory_usage,
                last_used=last_used,
                is_loaded=is_loaded
            ))

        return ModelsList(
            models=model_summaries,
            total_count=len(model_summaries),
            loaded_count=loaded_count
        )

    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve models list: {str(e)}"
        )


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

        # First check if model exists in configuration
        if model_id not in model_manager.config.get('models', {}):
            raise HTTPException(
                status_code=404,
                detail=f"Model {model_id} not found"
            )

        start_time = time.time()

        # Get model from manager (handles loading if needed)
        model = await model_manager.get_model(model_id)
        if model is None:
            raise HTTPException(
                status_code=500,
                detail=f"Model {model_id} failed to load"
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

        # Get active models count from model manager
        active_models = model_manager.active_model_count  # Use the new property
        logger.info(f"Current active models: {active_models}")

        return SystemStatus(
            active_models=active_models,  # Use the count from model manager
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
