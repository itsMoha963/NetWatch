from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AlertType(str, Enum):
    DEVICE_OFFLINE = "device_offline"
    HIGH_CPU = "high_cpu"
    HIGH_MEMORY = "high_memory"
    HIGH_LATENCY = "high_latency"


class AlertSeverity(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index(
            "uq_alerts_unresolved_device_type",
            "device_id",
            "alert_type",
            unique=True,
            postgresql_where=text("resolved = false"),
        ),
        Index(
            "ix_alerts_device_resolved_created",
            "device_id",
            "resolved",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
    )
    alert_type: Mapped[AlertType] = mapped_column(
        SqlEnum(
            AlertType,
            name="alert_type_enum",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        SqlEnum(
            AlertSeverity,
            name="alert_severity_enum",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    resolved: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default="false",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
