from app.models.device import Device
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceResponse


class PersistentDeviceService:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def get_by_id(self, device_id: int) -> DeviceResponse | None:
        device = self._repository.get_by_id(device_id)

        if device is None:
            return None

        return DeviceResponse.model_validate(device)

    def list_all(self) -> list[DeviceResponse]:
        devices = self._repository.list_all()

        return [
            DeviceResponse.model_validate(device)
            for device in devices
        ]

    def create(self, device_data: DeviceCreate) -> DeviceResponse:
        device = Device(
            name=device_data.name,
            hostname=device_data.hostname,
            ip_address=str(device_data.ip_address),
            device_type=device_data.device_type.value,
        )

        created_device = self._repository.create(device)

        return DeviceResponse.model_validate(created_device)

    def delete(self, device_id: int) -> bool:
        return self._repository.delete(device_id)

    def replace(
        self,
        device_id: int,
        replacement: DeviceCreate,
    ) -> DeviceResponse | None:
        existing_device = self._repository.get_by_id(device_id)

        if existing_device is None:
            return None

        existing_device.name = replacement.name
        existing_device.hostname = replacement.hostname
        existing_device.ip_address = str(replacement.ip_address)
        existing_device.device_type = replacement.device_type.value

        saved_device = self._repository.save(existing_device)

        return DeviceResponse.model_validate(saved_device)
