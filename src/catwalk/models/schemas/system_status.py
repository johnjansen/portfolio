from pydantic import BaseModel


class SystemStatus(BaseModel):
    """System-wide status information"""
    active_models: int
    total_memory_usage: str
    cache_utilization: float
    healthy: bool
    uptime: str
