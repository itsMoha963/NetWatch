from fastapi.testclient import TestClient

from app.main import app

def test_create_then_list_devices():
    client = TestClient(app)

    initial_response = client.get("/devices")
    initial_count = len(initial_response.json())

    create_response = client.post(
        "/devices",
        json={
            "name": "Home-Rounter",
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