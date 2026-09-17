import os
from uuid import uuid4

import pytest

from app.db.session import session_factory, settings
from app.models.device import Device
from app.models.metric import Metric
from app.repositories.device_repository import DeviceRepository
from app.repositories.metric_repository import MetricRepository


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1",
        reason="database integration tests are disabled",
    ),
]


def test_metric_repository_create_and_list_for_device():
    assert settings.postgres_db == "netwatch_test"

    unique_number = uuid4().int
    hostname = f"metric-test-{unique_number:x}"
    ip_address = (
        f"10.201.{(unique_number >> 8) % 254 + 1}."
        f"{unique_number % 254 + 1}"
    )

    with session_factory() as session:
        device_repository = DeviceRepository(session)
        metric_repository = MetricRepository(session)
        device = device_repository.create(
            Device(
                name="Metric Test Device",
                hostname=hostname,
                ip_address=ip_address,
                device_type="server",
            )
        )

        try:
            first_metric = metric_repository.create(
                Metric(
                    device_id=device.id,
                    cpu_usage=20.0,
                    memory_usage=40.0,
                    latency_ms=12.0,
                    uptime_seconds=100,
                )
            )
            second_metric = metric_repository.create(
                Metric(
                    device_id=device.id,
                    cpu_usage=30.0,
                    memory_usage=50.0,
                    latency_ms=10.0,
                    uptime_seconds=200,
                )
            )

            history = metric_repository.list_for_device(device.id)

            assert [metric.id for metric in history] == [
                second_metric.id,
                first_metric.id,
            ]
            assert all(metric.device_id == device.id for metric in history)
        finally:
            device_repository.delete(device.id)

        assert metric_repository.list_for_device(device.id) == []
