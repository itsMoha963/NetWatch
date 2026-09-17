from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import session_factory
from app.repositories.device_repository import DeviceRepository
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
