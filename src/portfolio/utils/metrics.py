# src/portfolio/utils/metrics.py
from dataclasses import dataclass, field
from typing import Dict, Any, List
import time
import psutil
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Track per-model metrics"""
    load_time: float = 0.0
    inference_times: List[float] = field(default_factory=list)
    memory_usage: int = 0
    request_count: int = 0  # Add explicit request counter
    hits: int = 0
    misses: int = 0


class MetricsCollector:
    """System-wide metrics collection"""

    def __init__(self):
        self.model_metrics: Dict[str, ModelMetrics] = {}
        self.start_time = time.time()
        self._total_requests = 0  # Add global request counter
        logger.info("MetricsCollector initialized")

    def record_inference(self, model_id: str, duration: float):
        """Record a model inference"""
        try:
            if model_id not in self.model_metrics:
                self.model_metrics[model_id] = ModelMetrics()

            metrics = self.model_metrics[model_id]
            metrics.inference_times.append(duration)
            metrics.request_count += 1
            self._total_requests += 1

            logger.debug(f"Recorded inference for {model_id}: duration={duration:.3f}s, "
                        f"total_requests={self._total_requests}")
        except Exception as e:
            logger.error(f"Failed to record inference metrics: {str(e)}")

    def get_request_count(self) -> int:
        """Get total number of requests across all models"""
        return self._total_requests

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        return {
            'memory_usage': psutil.Process().memory_info().rss,
            'cpu_percent': psutil.cpu_percent(),
            'uptime': time.time() - self.start_time,
            'total_requests': self._total_requests
        }

    def get_inference_time_avg(self, model_id: str) -> float:
        """Calculate average inference time for a model"""
        try:
            if model_id not in self.model_metrics:
                return 0.0
            times = self.model_metrics[model_id].inference_times
            if not times:
                return 0.0
            return sum(times) / len(times)
        except Exception as e:
            logger.error(f"Failed to calculate average inference time: {str(e)}")
            return 0.0

    def get_model_metrics(self, model_id: str) -> Dict[str, Any]:
        """Get detailed metrics for a specific model"""
        if model_id not in self.model_metrics:
            return {}

        metrics = self.model_metrics[model_id]
        return {
            'request_count': metrics.request_count,
            'average_latency': self.get_inference_time_avg(model_id),
            'memory_usage': metrics.memory_usage,
            'hits': metrics.hits,
            'misses': metrics.misses
        }
