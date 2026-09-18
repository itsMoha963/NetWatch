from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_alert_service
from app.schemas.alert import AlertResponse
from app.services.alert_service import AlertService


AlertServiceDep = Annotated[
    AlertService,
    Depends(get_alert_service),
]

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    service: AlertServiceDep,
    resolved: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[AlertResponse]:
    return service.list_alerts(resolved, limit)


@router.get("/devices/{device_id}", response_model=list[AlertResponse])
async def list_device_alerts(
    device_id: int,
    service: AlertServiceDep,
    resolved: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[AlertResponse]:
    return service.list_for_device(device_id, resolved, limit)
