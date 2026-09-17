from collections.abc import Callable
from datetime import UTC, datetime

from app.services.metric_service import MetricService
from app.services.persistent_device_service import PersistentDeviceService
from app.simulator.device_simulator import DeviceSimulator


class MonitoringWorker:
    def __init__(
        self,
        device_service: PersistentDeviceService,
        metric_service: MetricService,
        simulator: DeviceSimulator,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._device_service = device_service
        self._metric_service = metric_service
        self._simulator = simulator
        self._clock = clock or (lambda: datetime.now(UTC))

    def run_once(self) -> int:
        processed_count = 0

        for device in self._device_service.list_all():
            result = self._simulator.simulate(device.id)

            updated_device = (
                self._device_service.update_monitoring_status(
                    device.id,
                    result.status,
                    self._clock(),
                )
            )

            if updated_device is None:
                continue

            if result.metric is not None:
                self._metric_service.create(
                    device.id,
                    result.metric,
                )

            processed_count += 1

        return processed_count