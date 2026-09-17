from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MetricCreate(BaseModel):
    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100)
    latency_ms: float = Field(ge=0)
    uptime_seconds: int = Field(ge=0)


class MetricResponse(MetricCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    recorded_at: datetime
