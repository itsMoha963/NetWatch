from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class DeviceType(str, Enum):
    ROUTER = "router"
    SERVER = "server"
    SWITCH = "switch"


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    hostname: str = Field(min_length=1, max_length=255)
    ip_address: IPvAnyAddress
    device_type: DeviceType


class DeviceStatus(str, Enum):
    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"


class DeviceResponse(DeviceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: DeviceStatus
    last_seen: datetime | None = None
    created_at: datetime
