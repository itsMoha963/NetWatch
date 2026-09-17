from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_device_service
from app.schemas.device import DeviceCreate, DeviceResponse
from app.services.persistent_device_service import PersistentDeviceService

DeviceServiceDep = Annotated[
    PersistentDeviceService,
    Depends(get_device_service),
]

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_device(
    device: DeviceCreate,
    service: DeviceServiceDep,
) -> DeviceResponse:
    return service.create(device)


@router.get("", response_model=list[DeviceResponse])
async def list_devices(
    service: DeviceServiceDep,
) -> list[DeviceResponse]:
    return service.list_all()


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    service: DeviceServiceDep,
) -> DeviceResponse:
    device = service.get_by_id(device_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )

    return device


@router.put("/{device_id}", response_model=DeviceResponse)
async def replace_device(
    device_id: int,
    replacement: DeviceCreate,
    service: DeviceServiceDep,
) -> DeviceResponse:
    replaced_device = service.replace(device_id, replacement)

    if replaced_device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )

    return replaced_device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    service: DeviceServiceDep,
) -> None:
    deleted = service.delete(device_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )
