from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import session_factory
from app.repositories.alert_repository import AlertRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.metric_repository import MetricRepository
from app.services.alert_service import AlertService
from app.services.metric_service import MetricService
from app.services.persistent_device_service import PersistentDeviceService


def get_db_session() -> Iterator[Session]:
    with session_factory() as session:
        yield session


def get_device_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> DeviceRepository:
    return DeviceRepository(session)


def get_device_service(
    repository: Annotated[
        DeviceRepository,
        Depends(get_device_repository),
    ],
) -> PersistentDeviceService:
    return PersistentDeviceService(repository)


def get_metric_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> MetricRepository:
    return MetricRepository(session)


def get_metric_service(
    metric_repository: Annotated[
        MetricRepository,
        Depends(get_metric_repository),
    ],
    device_repository: Annotated[
        DeviceRepository,
        Depends(get_device_repository),
    ],
) -> MetricService:
    return MetricService(
        metric_repository,
        device_repository,
    )


def get_alert_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> AlertRepository:
    return AlertRepository(session)


def get_alert_service(
    repository: Annotated[
        AlertRepository,
        Depends(get_alert_repository),
    ],
) -> AlertService:
    return AlertService(repository)
