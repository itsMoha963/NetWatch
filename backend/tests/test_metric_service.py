from datetime import UTC, datetime
from unittest.mock import Mock

from app.models.metric import Metric
from app.repositories.device_repository import DeviceRepository
from app.repositories.metric_repository import MetricRepository
from app.schemas.metric import MetricCreate
from app.services.metric_service import MetricService


def build_service() -> tuple[MetricService, Mock, Mock]:
    metric_repository = Mock(spec=MetricRepository)
    device_repository = Mock(spec=DeviceRepository)
    service = MetricService(metric_repository, device_repository)
    return service, metric_repository, device_repository


def metric_data() -> MetricCreate:
    return MetricCreate(
        cpu_usage=35.5,
        memory_usage=48.0,
        latency_ms=12.5,
        uptime_seconds=3600,
    )


def test_create_returns_none_for_missing_device():
    service, metric_repository, device_repository = build_service()
    device_repository.get_by_id.return_value = None

    result = service.create(999, metric_data())

    assert result is None
    metric_repository.create.assert_not_called()


def test_create_returns_persisted_metric():
    service, metric_repository, device_repository = build_service()
    device_repository.get_by_id.return_value = object()
    metric_repository.create.return_value = Metric(
        id=1,
        device_id=7,
        cpu_usage=35.5,
        memory_usage=48.0,
        latency_ms=12.5,
        uptime_seconds=3600,
        recorded_at=datetime.now(UTC),
    )

    result = service.create(7, metric_data())

    assert result is not None
    assert result.id == 1
    assert result.device_id == 7
    assert result.cpu_usage == 35.5


def test_list_returns_empty_list_for_device_without_metrics():
    service, metric_repository, device_repository = build_service()
    device_repository.get_by_id.return_value = object()
    metric_repository.list_for_device.return_value = []

    result = service.list_for_device(7)

    assert result == []
    metric_repository.list_for_device.assert_called_once_with(7, 100)
