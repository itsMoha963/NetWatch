from datetime import UTC, datetime

from app.schemas.device import DeviceCreate, DeviceResponse, DeviceStatus


class DeviceService:
    def __init__(self) -> None:
        self._devices: dict[int, DeviceResponse] = {}
        self._next_id: int = 1

    def create(self, device: DeviceCreate) -> DeviceResponse:
        created_device = DeviceResponse(
            id=self._next_id,
            name=device.name,
            hostname=device.hostname,
            ip_address=device.ip_address,
            device_type=device.device_type,
            status=DeviceStatus.UNKNOWN,
            created_at=datetime.now(UTC),
        )

        self._devices[created_device.id] = created_device
        self._next_id += 1

        return created_device

    def list_all(self) -> list[DeviceResponse]:
        return list(self._devices.values())

    def get_by_id(self, device_id: int) -> DeviceResponse | None:
        return self._devices.get(device_id)

    def replace(
        self,
        device_id: int,
        replacement: DeviceCreate,
    ) -> DeviceResponse | None:
        existing_device = self.get_by_id(device_id)

        if existing_device is None:
            return None

        replaced_device = DeviceResponse(
            id=existing_device.id,
            name=replacement.name,
            hostname=replacement.hostname,
            ip_address=replacement.ip_address,
            device_type=replacement.device_type,
            status=existing_device.status,
            last_seen=existing_device.last_seen,
            created_at=existing_device.created_at,
        )

        self._devices[device_id] = replaced_device
        return replaced_device
