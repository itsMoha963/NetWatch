from fastapi import APIRouter, status

from app.schemas.device import DeviceCreate, DeviceResponse
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["Devices"])
device_service = DeviceService()


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_device(device: DeviceCreate) -> DeviceResponse:
    return device_service.create(device)


@router.get("", response_model=list[DeviceResponse])
async def list_devices() -> list[DeviceResponse]:
    return device_service.list_all()