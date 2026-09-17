from datetime import UTC, datetime
from unittest.mock import Mock

from app.schemas.device import DeviceStatus
from app.schemas.metric import MetricCreate
from app.services.metric_service import MetricService
from app.services.persistent_device_service import PersistentDeviceService
from app.simulator.device_simulator import DeviceSimulator, SimulationResult
from app.workers.monitoring_worker import MonitoringWorker


def build_worker(result: SimulationResult, updated_device=object()):
    device_service = Mock(spec=PersistentDeviceService)
    metric_service = Mock(spec=MetricService)
    simulator = Mock(spec=DeviceSimulator)
    device_service.list_all.return_value = [Mock(id=1)]
    device_service.update_monitoring_status.return_value = updated_device
    simulator.simulate.return_value = result
    checked_at = datetime(2026, 9, 17, 12, 0, tzinfo=UTC)
    worker = MonitoringWorker(
        device_service,
        metric_service,
        simulator,
        clock=lambda: checked_at,
    )
    return worker, device_service, metric_service, simulator, checked_at


def test_online_result_updates_device_and_stores_metric():
    metric = MetricCreate(
        cpu_usage=43,
        memory_usage=61,
        latency_ms=15,
        uptime_seconds=30,
    )
    result = SimulationResult(DeviceStatus.ONLINE, metric)
    worker, device_service, metric_service, simulator, checked_at = (
        build_worker(result)
    )

    processed_count = worker.run_once()

    assert processed_count == 1
    simulator.simulate.assert_called_once_with(1)
    device_service.update_monitoring_status.assert_called_once_with(
        1,
        DeviceStatus.ONLINE,
        checked_at,
    )
    metric_service.create.assert_called_once_with(1, metric)


def test_offline_result_updates_device_without_storing_metric():
    result = SimulationResult(DeviceStatus.OFFLINE, None)
    worker, device_service, metric_service, _, checked_at = build_worker(
        result
    )

    processed_count = worker.run_once()

    assert processed_count == 1
    device_service.update_monitoring_status.assert_called_once_with(
        1,
        DeviceStatus.OFFLINE,
        checked_at,
    )
    metric_service.create.assert_not_called()


def test_worker_skips_device_deleted_during_monitoring():
    metric = MetricCreate(
        cpu_usage=43,
        memory_usage=61,
        latency_ms=15,
        uptime_seconds=30,
    )
    result = SimulationResult(DeviceStatus.ONLINE, metric)
    worker, _, metric_service, _, _ = build_worker(
        result,
        updated_device=None,
    )

    processed_count = worker.run_once()

    assert processed_count == 0
    metric_service.create.assert_not_called()
