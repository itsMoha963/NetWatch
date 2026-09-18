import argparse
import logging
import time

from app.db.session import session_factory
from app.repositories.alert_repository import AlertRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.metric_repository import MetricRepository
from app.services.alert_service import AlertService
from app.services.metric_service import MetricService
from app.services.persistent_device_service import PersistentDeviceService
from app.simulator.device_simulator import DeviceSimulator
from app.workers.monitoring_worker import MonitoringWorker

logger = logging.getLogger(__name__)


def run_cycle(simulator: DeviceSimulator) -> int:
    with session_factory() as session:
        device_repository = DeviceRepository(session)
        metric_repository = MetricRepository(session)
        alert_repository = AlertRepository(session)
        device_service = PersistentDeviceService(device_repository)
        metric_service = MetricService(
            metric_repository,
            device_repository,
        )
        alert_service = AlertService(alert_repository)
        worker = MonitoringWorker(
            device_service,
            metric_service,
            alert_service,
            simulator,
        )

        return worker.run_once()


def run_monitoring(cycles: int, interval_seconds: float) -> None:
    simulator = DeviceSimulator()
    completed_cycles = 0

    try:
        while cycles == 0 or completed_cycles < cycles:
            processed_count = run_cycle(simulator)
            completed_cycles += 1
            logger.info(
                f"Monitoring cycle {completed_cycles} complete: "
                f"{processed_count} devices processed"
            )

            if cycles != 0 and completed_cycles >= cycles:
                break

            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run simulated NetWatch monitoring cycles.",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="number of cycles to run; use 0 to run continuously",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=30,
        help="seconds to wait between cycles",
    )
    args = parser.parse_args()

    if args.cycles < 0:
        parser.error("--cycles must be 0 or greater")

    if args.interval <= 0:
        parser.error("--interval must be greater than 0")

    return args


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args = parse_args()

    run_monitoring(args.cycles, args.interval)


if __name__ == "__main__":
    main()
from app.services.alert_service import AlertService
