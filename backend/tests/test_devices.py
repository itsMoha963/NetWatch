from fastapi.testclient import TestClient

from app.main import app


def test_create_then_list_devices():
    client = TestClient(app)

    initial_response = client.get("/devices")
    initial_count = len(initial_response.json())

    create_response = client.post(
        "/devices",
        json={
            "name": "Home-Router",
            "hostname": "home-router",
            "ip_address": "192.168.1.1",
            "device_type": "router",
        },
    )

    list_response = client.get("/devices")
    listed_devices = list_response.json()

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert len(listed_devices) == initial_count + 1
    assert create_response.json() in listed_devices


def test_get_existing_device():
    client = TestClient(app)

    create_response = client.post(
        "/devices",
        json={
            "name": "Server-Berlin",
            "hostname": "server-berlin",
            "ip_address": "10.0.0.10",
            "device_type": "server",
        },
    )
    created_device = create_response.json()

    response = client.get(f"/devices/{created_device['id']}")

    assert response.status_code == 200
    assert response.json() == created_device


def test_get_missing_device():
    client = TestClient(app)

    response = client.get("/devices/92929")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Device with ID 92929 not found"
    }
