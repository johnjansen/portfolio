# src/catwalk/utils/monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time


class ModelMetrics:
    def __init__(self):
        self.inference_latency = Histogram(
            'model_inference_latency_seconds',
            'Model inference latency',
            ['model_id']
        )
        self.inference_count = Counter(
            'model_inference_total',
            'Total number of model inferences',
            ['model_id']
        )
        self.memory_usage = Gauge(
            'model_memory_bytes',
            'Current model memory usage',
            ['model_id']
        )

    def record_inference(self, model_id: str, start_time: float):
        duration = time.time() - start_time
        self.inference_latency.labels(model_id).observe(duration)
        self.inference_count.labels(model_id).inc()
