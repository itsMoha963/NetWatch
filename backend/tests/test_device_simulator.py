import random
from unittest.mock import Mock

from app.schemas.device import DeviceStatus
from app.simulator.device_simulator import DeviceSimulator


def test_simulator_tracks_uptime_per_device():
    random_generator = Mock(spec=random.Random)
    random_generator.random.return_value = 0.5
    random_generator.uniform.return_value = 20.0
    simulator = DeviceSimulator(random_generator)

    first_device_result = simulator.simulate(1)
    second_device_result = simulator.simulate(2)
    next_first_device_result = simulator.simulate(1)

    assert first_device_result.metric is not None
    assert second_device_result.metric is not None
    assert next_first_device_result.metric is not None
    assert first_device_result.metric.uptime_seconds == 30
    assert second_device_result.metric.uptime_seconds == 30
    assert next_first_device_result.metric.uptime_seconds == 60


def test_offline_result_resets_device_uptime():
    random_generator = Mock(spec=random.Random)
    random_generator.random.return_value = 0.5
    random_generator.uniform.return_value = 20.0
    simulator = DeviceSimulator(random_generator)

    simulator.OFFLINE_PROBABILITY = 0
    simulator.simulate(1)

    simulator.OFFLINE_PROBABILITY = 1
    offline_result = simulator.simulate(1)

    simulator.OFFLINE_PROBABILITY = 0
    online_result = simulator.simulate(1)

    assert offline_result.status is DeviceStatus.OFFLINE
    assert offline_result.metric is None
    assert online_result.metric is not None
    assert online_result.metric.uptime_seconds == 30


def test_simulator_can_generate_anomalies():
    random_generator = Mock(spec=random.Random)
    random_generator.random.return_value = 0.5
    random_generator.uniform.side_effect = [90.0, 95.0, 300.0]
    simulator = DeviceSimulator(random_generator)
    simulator.OFFLINE_PROBABILITY = 0
    simulator.ANOMALY_PROBABILITY = 1

    result = simulator.simulate(1)

    assert result.status is DeviceStatus.ONLINE
    assert result.metric is not None
    assert result.metric.cpu_usage == 90.0
    assert result.metric.memory_usage == 95.0
    assert result.metric.latency_ms == 300.0
