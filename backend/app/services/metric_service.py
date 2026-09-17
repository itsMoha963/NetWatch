from app.models.metric import Metric
from app.repositories.device_repository import DeviceRepository
from app.repositories.metric_repository import MetricRepository
from app.schemas.metric import MetricCreate, MetricResponse


class MetricService:
    def __init__(
        self,
        metric_repository: MetricRepository,
        device_repository: DeviceRepository,
    ) -> None:
        self._metric_repository = metric_repository
        self._device_repository = device_repository

    def create(
        self,
        device_id: int,
        metric_data: MetricCreate,
    ) -> MetricResponse | None:
        if self._device_repository.get_by_id(device_id) is None:
            return None

        metric = Metric(
            device_id=device_id,
            cpu_usage=metric_data.cpu_usage,
            memory_usage=metric_data.memory_usage,
            latency_ms=metric_data.latency_ms,
            uptime_seconds=metric_data.uptime_seconds,
        )
        created_metric = self._metric_repository.create(metric)

        return MetricResponse.model_validate(created_metric)

    def list_for_device(
        self,
        device_id: int,
        limit: int = 100,
    ) -> list[MetricResponse] | None:
        if self._device_repository.get_by_id(device_id) is None:
            return None

        metrics = self._metric_repository.list_for_device(
            device_id,
            limit,
        )

        return [
            MetricResponse.model_validate(metric)
            for metric in metrics
        ]
