import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.session import session_factory, settings
from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.device import Device
from app.repositories.alert_repository import AlertRepository
from app.repositories.device_repository import DeviceRepository


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1",
        reason="database integration tests are disabled",
    ),
]


def test_unresolved_alerts_are_unique_per_device_and_type():
    assert settings.postgres_db == "netwatch_test"

    unique_number = uuid4().int
    hostname = f"alert-test-{unique_number:x}"
    ip_address = (
        f"10.202.{(unique_number >> 8) % 254 + 1}."
        f"{unique_number % 254 + 1}"
    )

    with session_factory() as session:
        device_repository = DeviceRepository(session)
        alert_repository = AlertRepository(session)
        device = device_repository.create(
            Device(
                name="Alert Test Device",
                hostname=hostname,
                ip_address=ip_address,
                device_type="router",
            )
        )
        alert = Alert(
            device_id=device.id,
            alert_type=AlertType.HIGH_CPU,
            severity=AlertSeverity.WARNING,
            message="CPU is high",
            created_at=datetime.now(UTC),
        )

        try:
            first = alert_repository.create(alert)
            assert alert_repository.get_unresolved(
                device.id,
                AlertType.HIGH_CPU,
            ) is not None

            with pytest.raises(IntegrityError):
                alert_repository.create(
                    Alert(
                        device_id=device.id,
                        alert_type=AlertType.HIGH_CPU,
                        severity=AlertSeverity.WARNING,
                        message="CPU is still high",
                    )
                )
            session.rollback()

            first.resolved = True
            first.resolved_at = datetime.now(UTC)
            alert_repository.save(first)

            second = alert_repository.create(
                Alert(
                    device_id=device.id,
                    alert_type=AlertType.HIGH_CPU,
                    severity=AlertSeverity.WARNING,
                    message="CPU is high again",
                )
            )
            assert second.id != first.id
        finally:
            device_repository.delete(device.id)
