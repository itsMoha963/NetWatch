import random
from dataclasses import dataclass

from app.schemas.device import DeviceStatus
from app.schemas.metric import MetricCreate


@dataclass(frozen=True)
class SimulationResult:
    status: DeviceStatus
    metric: MetricCreate | None


class DeviceSimulator:
    OFFLINE_PROBABILITY = 0.1
    INTERVAL_SECONDS = 30
    ANOMALY_PROBABILITY = 0.1

    def __init__(
        self,
        random_generator: random.Random | None = None,
    ) -> None:
        self._random = random_generator or random.Random()
        self._uptime_by_device: dict[int, int] = {}

    def simulate(self, device_id: int) -> SimulationResult:
        if self._random.random() < self.OFFLINE_PROBABILITY:
            self._uptime_by_device[device_id] = 0
            return SimulationResult(
                status=DeviceStatus.OFFLINE,
                metric=None,
            )

        uptime = (
            self._uptime_by_device.get(device_id, 0)
            + self.INTERVAL_SECONDS
        )
        self._uptime_by_device[device_id] = uptime

        metric = MetricCreate(
            cpu_usage=self._generate_value(5, 75, 80, 100),
            memory_usage=self._generate_value(10, 85, 90, 100),
            latency_ms=self._generate_value(1, 80, 150, 500),
            uptime_seconds=uptime,
        )

        return SimulationResult(
            status=DeviceStatus.ONLINE,
            metric=metric,
        )

    def _generate_value(
        self,
        normal_min: float,
        normal_max: float,
        anomaly_min: float,
        anomaly_max: float,
    ) -> float:
        if self._random.random() < self.ANOMALY_PROBABILITY:
            minimum = anomaly_min
            maximum = anomaly_max
        else:
            minimum = normal_min
            maximum = normal_max

        return round(self._random.uniform(minimum, maximum), 2)
