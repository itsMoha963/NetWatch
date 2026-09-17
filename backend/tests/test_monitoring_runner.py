from unittest.mock import patch

from app.workers.run_monitoring import run_monitoring


@patch("app.workers.run_monitoring.time.sleep")
@patch("app.workers.run_monitoring.run_cycle", return_value=3)
def test_run_monitoring_runs_requested_cycles(run_cycle, sleep):
    run_monitoring(cycles=2, interval_seconds=5)

    assert run_cycle.call_count == 2
    sleep.assert_called_once_with(5)


@patch("app.workers.run_monitoring.time.sleep")
@patch(
    "app.workers.run_monitoring.run_cycle",
    side_effect=[3, KeyboardInterrupt],
)
def test_continuous_monitoring_stops_on_keyboard_interrupt(
    run_cycle,
    sleep,
):
    run_monitoring(cycles=0, interval_seconds=5)

    assert run_cycle.call_count == 2
    sleep.assert_called_once_with(5)
