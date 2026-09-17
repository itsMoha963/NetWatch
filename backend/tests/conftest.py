import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_device_service
from app.main import app
from app.services.device_service import DeviceService


@pytest.fixture
def client():
    test_service = DeviceService()
    app.dependency_overrides[get_device_service] = lambda: test_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
