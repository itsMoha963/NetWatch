from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class AlertType(str, Enum):
    DEVICE_OFFLINE = "device_offline"
    HIGH_CPU = "high_cpu"
    HIGH_MEMORY = "high_memory"
    HIGH_LATENCY = "high_latency"


class AlertSeverity(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    resolved: bool
    created_at: datetime
    resolved_at: datetime | None = None
