# src/catwalk/utils/metrics.py
from dataclasses import dataclass
from typing import Dict, Any
import time
import psutil


@dataclass
class ModelMetrics:
    """Track per-model metrics"""
    load_time: float
    inference_times: list[float]
    memory_usage: int
    hits: int
    misses: int


class MetricsCollector:
    """System-wide metrics collection"""

    def __init__(self):
        self.model_metrics: Dict[str, ModelMetrics] = {}
        self.start_time = time.time()

    def record_inference(self, model_id: str, duration: float):
        """Record a model inference"""
        if model_id not in self.model_metrics:
            self.model_metrics[model_id] = ModelMetrics(0, [], 0, 0, 0)
        self.model_metrics[model_id].inference_times.append(duration)

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        return {
            'memory_usage': psutil.Process().memory_info().rss,
            'cpu_percent': psutil.cpu_percent(),
            'uptime': time.time() - self.start_time
        }

    def get_request_count(self) -> int:
        """Get total number of requests across all models"""
        total = 0
        for metrics in self.model_metrics.values():
            total += metrics.hits + metrics.misses
        return total

    def get_inference_time_avg(self, model_id: str) -> float:
        """Calculate average inference time for a model"""
        if model_id not in self.model_metrics:
            return 0.0
        times = self.model_metrics[model_id].inference_times
        if not times:
            return 0.0
        return sum(times) / len(times)
