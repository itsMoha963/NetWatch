from datetime import UTC, datetime

from app.schemas.alert import AlertResponse, AlertSeverity, AlertType


def alert_response() -> AlertResponse:
    return AlertResponse(
        id=1,
        device_id=7,
        alert_type=AlertType.HIGH_MEMORY,
        severity=AlertSeverity.CRITICAL,
        message="memory is high",
        resolved=False,
        created_at=datetime.now(UTC),
    )


def test_list_alerts(client, alert_service):
    alert_service.list_alerts.return_value = [alert_response()]

    response = client.get("/alerts?resolved=false&limit=25")

    assert response.status_code == 200
    assert response.json()[0]["alert_type"] == "high_memory"
    alert_service.list_alerts.assert_called_once_with(False, 25)


def test_list_device_alerts(client, alert_service):
    alert_service.list_for_device.return_value = [alert_response()]

    response = client.get("/alerts/devices/7?resolved=false")

    assert response.status_code == 200
    assert response.json()[0]["device_id"] == 7
    alert_service.list_for_device.assert_called_once_with(7, False, 100)
