from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hostname: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        unique=True,
    )
    device_type: Mapped[str] = mapped_column(
        Enum(
            "router",
            "server",
            "switch",
            name="device_type_enum",
        ),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "unknown",
            "online",
            "offline",
            name="device_status_enum",
        ),
        nullable=False,
        default="unknown",
        server_default="unknown",
    )
    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
