from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Metric(Base):
    __tablename__ = "metrics"
    __table_args__ = (
        CheckConstraint(
            "cpu_usage BETWEEN 0 AND 100",
            name="ck_metrics_cpu_usage_range",
        ),
        CheckConstraint(
            "memory_usage BETWEEN 0 AND 100",
            name="ck_metrics_memory_usage_range",
        ),
        CheckConstraint(
            "latency_ms >= 0",
            name="ck_metrics_latency_nonnegative",
        ),
        CheckConstraint(
            "uptime_seconds >= 0",
            name="ck_metrics_uptime_nonnegative",
        ),
        Index(
            "ix_metrics_device_recorded_at",
            "device_id",
            "recorded_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
    )
    cpu_usage: Mapped[float] = mapped_column(Float, nullable=False)
    memory_usage: Mapped[float] = mapped_column(Float, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    uptime_seconds: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
