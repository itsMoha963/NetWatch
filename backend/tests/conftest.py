from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_device_service, get_metric_service
from app.main import app
from app.services.device_service import DeviceService
from app.services.metric_service import MetricService


@pytest.fixture
def metric_service():
    return Mock(spec=MetricService)


@pytest.fixture
def client(metric_service):
    test_service = DeviceService()
    app.dependency_overrides[get_device_service] = lambda: test_service
    app.dependency_overrides[get_metric_service] = lambda: metric_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
