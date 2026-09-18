from collections.abc import Callable
from datetime import UTC, datetime

from app.services.alert_service import AlertService
from app.services.metric_service import MetricService
from app.services.persistent_device_service import PersistentDeviceService
from app.simulator.device_simulator import DeviceSimulator


class MonitoringWorker:
    def __init__(
        self,
        device_service: PersistentDeviceService,
        metric_service: MetricService,
        alert_service: AlertService,
        simulator: DeviceSimulator,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._device_service = device_service
        self._metric_service = metric_service
        self._alert_service = alert_service
        self._simulator = simulator
        self._clock = clock or (lambda: datetime.now(UTC))

    def run_once(self) -> int:
        processed_count = 0

        for device in self._device_service.list_all():
            result = self._simulator.simulate(device.id)
            checked_at = self._clock()

            updated_device = (
                self._device_service.update_monitoring_status(
                    device.id,
                    result.status,
                    checked_at,
                )
            )

            if updated_device is None:
                continue

            if result.metric is not None:
                self._metric_service.create(
                    device.id,
                    result.metric,
                )

            self._alert_service.evaluate(
                device.id,
                result.status,
                result.metric,
                checked_at,
            )

            processed_count += 1

        return processed_count
