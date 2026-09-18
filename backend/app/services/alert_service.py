from dataclasses import dataclass
from datetime import UTC, datetime

from app.models.alert import Alert, AlertSeverity, AlertType
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertResponse
from app.schemas.device import DeviceStatus
from app.schemas.metric import MetricCreate


@dataclass(frozen=True)
class AlertThresholds:
    cpu_warning: float = 80
    memory_critical: float = 90
    latency_warning_ms: float = 200


class AlertService:
    def __init__(
        self,
        repository: AlertRepository,
        thresholds: AlertThresholds | None = None,
    ) -> None:
        self._repository = repository
        self._thresholds = thresholds or AlertThresholds()

    def evaluate(
        self,
        device_id: int,
        status: DeviceStatus,
        metric: MetricCreate | None,
        checked_at: datetime | None = None,
    ) -> list[AlertResponse]:
        checked_at = checked_at or datetime.now(UTC)
        conditions: list[tuple[AlertType, AlertSeverity, str, bool]] = [
            (
                AlertType.DEVICE_OFFLINE,
                AlertSeverity.CRITICAL,
                f"Device {device_id} is offline",
                status is DeviceStatus.OFFLINE,
            )
        ]

        if status is DeviceStatus.ONLINE and metric is not None:
            conditions.extend(
                [
                    (
                        AlertType.HIGH_CPU,
                        AlertSeverity.WARNING,
                        f"Device {device_id} CPU usage is {metric.cpu_usage:.2f}%",
                        metric.cpu_usage > self._thresholds.cpu_warning,
                    ),
                    (
                        AlertType.HIGH_MEMORY,
                        AlertSeverity.CRITICAL,
                        f"Device {device_id} memory usage is {metric.memory_usage:.2f}%",
                        metric.memory_usage > self._thresholds.memory_critical,
                    ),
                    (
                        AlertType.HIGH_LATENCY,
                        AlertSeverity.WARNING,
                        f"Device {device_id} latency is {metric.latency_ms:.2f} ms",
                        metric.latency_ms > self._thresholds.latency_warning_ms,
                    ),
                ]
            )

        changed_alerts: list[AlertResponse] = []
        for alert_type, severity, message, active in conditions:
            existing = self._repository.get_unresolved(device_id, alert_type)

            if active and existing is None:
                created = self._repository.create(
                    Alert(
                        device_id=device_id,
                        alert_type=alert_type,
                        severity=severity,
                        message=message,
                    )
                )
                changed_alerts.append(AlertResponse.model_validate(created))
            elif not active and existing is not None:
                resolved = self._repository.resolve(existing, checked_at)
                changed_alerts.append(AlertResponse.model_validate(resolved))

        return changed_alerts

    def list_alerts(
        self,
        resolved: bool | None = None,
        limit: int = 100,
    ) -> list[AlertResponse]:
        alerts = self._repository.list_all(resolved, limit)
        return [AlertResponse.model_validate(alert) for alert in alerts]

    def list_for_device(
        self,
        device_id: int,
        resolved: bool | None = None,
        limit: int = 100,
    ) -> list[AlertResponse]:
        alerts = self._repository.list_for_device(device_id, resolved, limit)
        return [AlertResponse.model_validate(alert) for alert in alerts]
