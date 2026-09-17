from datetime import UTC, datetime

from app.schemas.metric import MetricResponse


def metric_response() -> MetricResponse:
    return MetricResponse(
        id=1,
        device_id=7,
        cpu_usage=43.5,
        memory_usage=61.2,
        latency_ms=15.8,
        uptime_seconds=86400,
        recorded_at=datetime.now(UTC),
    )


def test_create_metric(client, metric_service):
    metric_service.create.return_value = metric_response()

    response = client.post(
        "/devices/7/metrics",
        json={
            "cpu_usage": 43.5,
            "memory_usage": 61.2,
            "latency_ms": 15.8,
            "uptime_seconds": 86400,
        },
    )

    assert response.status_code == 201
    assert response.json()["device_id"] == 7
    assert response.json()["cpu_usage"] == 43.5


def test_list_metric_history(client, metric_service):
    metric_service.list_for_device.return_value = [metric_response()]

    response = client.get("/devices/7/metrics?limit=25")

    assert response.status_code == 200
    assert len(response.json()) == 1
    metric_service.list_for_device.assert_called_once_with(7, 25)


def test_create_metric_for_missing_device(client, metric_service):
    metric_service.create.return_value = None

    response = client.post(
        "/devices/999/metrics",
        json={
            "cpu_usage": 43.5,
            "memory_usage": 61.2,
            "latency_ms": 15.8,
            "uptime_seconds": 86400,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Device with ID 999 not found"}


def test_create_metric_rejects_invalid_measurement(client, metric_service):
    response = client.post(
        "/devices/7/metrics",
        json={
            "cpu_usage": 101,
            "memory_usage": 61.2,
            "latency_ms": -1,
            "uptime_seconds": 86400,
        },
    )

    assert response.status_code == 422
    metric_service.create.assert_not_called()


def test_list_metrics_rejects_invalid_limit(client, metric_service):
    response = client.get("/devices/7/metrics?limit=0")

    assert response.status_code == 422
    metric_service.list_for_device.assert_not_called()
