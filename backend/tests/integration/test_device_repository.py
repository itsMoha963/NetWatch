import os
from uuid import uuid4

import pytest

from app.db.session import session_factory, settings
from app.models.device import Device
from app.repositories.device_repository import DeviceRepository


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1",
        reason="database integration tests are disabled",
    ),
]


def test_device_repository_crud():
    assert settings.postgres_db == "netwatch_test"

    unique_number = uuid4().int
    hostname = f"integration-test-{unique_number:x}"
    ip_address = (
        f"10.200.{(unique_number >> 8) % 254 + 1}."
        f"{unique_number % 254 + 1}"
    )

    with session_factory() as session:
        repository = DeviceRepository(session)
        created_device = repository.create(
            Device(
                name="Integration Test Router",
                hostname=hostname,
                ip_address=ip_address,
                device_type="router",
            )
        )

        try:
            assert created_device.id is not None
            assert created_device.status == "unknown"
            assert created_device.created_at is not None

            found_device = repository.get_by_id(created_device.id)
            assert found_device is not None
            assert found_device.hostname == hostname

            found_device.name = "Updated Integration Router"
            saved_device = repository.save(found_device)
            assert saved_device.name == "Updated Integration Router"

            listed_ids = [device.id for device in repository.list_all()]
            assert created_device.id in listed_ids

            assert repository.delete(created_device.id) is True
            assert repository.get_by_id(created_device.id) is None
            assert repository.delete(created_device.id) is False
        finally:
            repository.delete(created_device.id)
