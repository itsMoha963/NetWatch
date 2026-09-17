from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

from app.models.device import Device
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceStatus
from app.services.persistent_device_service import PersistentDeviceService


def test_monitoring_status_preserves_last_seen_when_device_goes_offline():
    repository = Mock(spec=DeviceRepository)
    device = Device(
        id=1,
        name="Test Router",
        hostname="test-router",
        ip_address="10.0.0.1",
        device_type="router",
        status="unknown",
        last_seen=None,
        created_at=datetime.now(UTC),
    )
    repository.get_by_id.return_value = device
    repository.save.side_effect = lambda saved_device: saved_device
    service = PersistentDeviceService(repository)
    online_time = datetime.now(UTC)

    online_result = service.update_monitoring_status(
        1,
        DeviceStatus.ONLINE,
        online_time,
    )
    offline_result = service.update_monitoring_status(
        1,
        DeviceStatus.OFFLINE,
        online_time + timedelta(minutes=1),
    )

    assert online_result is not None
    assert online_result.status is DeviceStatus.ONLINE
    assert offline_result is not None
    assert offline_result.status is DeviceStatus.OFFLINE
    assert offline_result.last_seen == online_time


def test_monitoring_status_returns_none_for_missing_device():
    repository = Mock(spec=DeviceRepository)
    repository.get_by_id.return_value = None
    service = PersistentDeviceService(repository)

    result = service.update_monitoring_status(
        999,
        DeviceStatus.OFFLINE,
        datetime.now(UTC),
    )

    assert result is None
    repository.save.assert_not_called()
