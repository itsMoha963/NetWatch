from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device import Device


class DeviceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, device_id: int) -> Device | None:
        return self._session.get(Device, device_id)

    def list_all(self) -> list[Device]:
        statement = select(Device).order_by(Device.id)
        return list(self._session.scalars(statement))

    def create(self, device: Device) -> Device:
        self._session.add(device)
        self._session.commit()
        self._session.refresh(device)
        return device

    def delete(self, device_id: int) -> bool:
        device = self.get_by_id(device_id)

        if device is None:
            return False

        self._session.delete(device)
        self._session.commit()
        return True

    def save(self, device: Device) -> Device:
        self._session.commit()
        self._session.refresh(device)
        return device
