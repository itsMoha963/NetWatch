from fastapi import APIRouter, HTTPException, status

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


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: int) -> DeviceResponse:
    device = device_service.get_by_id(device_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )

    return device