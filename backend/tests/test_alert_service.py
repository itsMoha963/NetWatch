from datetime import UTC, datetime
from unittest.mock import Mock

from app.models.alert import Alert, AlertSeverity, AlertType
from app.repositories.alert_repository import AlertRepository
from app.schemas.device import DeviceStatus
from app.schemas.metric import MetricCreate
from app.services.alert_service import AlertService


def build_alert(alert_type: AlertType, severity: AlertSeverity) -> Alert:
    return Alert(
        id=1,
        device_id=7,
        alert_type=alert_type,
        severity=severity,
        message="test alert",
        resolved=False,
        created_at=datetime.now(UTC),
    )


def persist_alert(alert: Alert) -> Alert:
    alert.id = 1
    alert.resolved = False
    alert.created_at = datetime.now(UTC)
    return alert


def test_high_metrics_create_one_alert_per_active_condition():
    repository = Mock(spec=AlertRepository)
    repository.get_unresolved.return_value = None
    repository.create.side_effect = persist_alert
    service = AlertService(repository)

    changed_alerts = service.evaluate(
        7,
        DeviceStatus.ONLINE,
        MetricCreate(
            cpu_usage=85,
            memory_usage=95,
            latency_ms=250,
            uptime_seconds=30,
        ),
    )

    assert [alert.alert_type for alert in changed_alerts] == [
        AlertType.HIGH_CPU,
        AlertType.HIGH_MEMORY,
        AlertType.HIGH_LATENCY,
    ]
    assert repository.create.call_count == 3


def test_offline_check_creates_critical_alert():
    repository = Mock(spec=AlertRepository)
    repository.get_unresolved.return_value = None
    repository.create.side_effect = persist_alert
    service = AlertService(repository)

    changed_alerts = service.evaluate(7, DeviceStatus.OFFLINE, None)

    assert len(changed_alerts) == 1
    assert changed_alerts[0].alert_type.value == AlertType.DEVICE_OFFLINE.value
    assert changed_alerts[0].severity.value == AlertSeverity.CRITICAL.value


def test_existing_alert_is_resolved_when_condition_is_healthy():
    repository = Mock(spec=AlertRepository)
    existing = build_alert(AlertType.HIGH_CPU, AlertSeverity.WARNING)
    repository.get_unresolved.side_effect = [
        None,
        existing,
        None,
        None,
    ]
    def resolve_alert(alert: Alert, resolved_at: datetime) -> Alert:
        alert.resolved = True
        alert.resolved_at = resolved_at
        return alert

    repository.resolve.side_effect = resolve_alert
    service = AlertService(repository)

    changed_alerts = service.evaluate(
        7,
        DeviceStatus.ONLINE,
        MetricCreate(
            cpu_usage=40,
            memory_usage=40,
            latency_ms=20,
            uptime_seconds=60,
        ),
    )

    assert len(changed_alerts) == 1
    assert changed_alerts[0].alert_type.value == AlertType.HIGH_CPU.value
    repository.resolve.assert_called_once()
