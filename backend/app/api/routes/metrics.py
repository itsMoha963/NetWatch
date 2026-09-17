from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_metric_service
from app.schemas.metric import MetricCreate, MetricResponse
from app.services.metric_service import MetricService


MetricServiceDep = Annotated[
    MetricService,
    Depends(get_metric_service),
]

router = APIRouter(
    prefix="/devices/{device_id}/metrics",
    tags=["Metrics"],
)


@router.post(
    "",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_metric(
    device_id: int,
    metric_data: MetricCreate,
    service: MetricServiceDep,
) -> MetricResponse:
    metric = service.create(device_id, metric_data)

    if metric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )

    return metric


@router.get("", response_model=list[MetricResponse])
async def list_metrics(
    device_id: int,
    service: MetricServiceDep,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[MetricResponse]:
    metrics = service.list_for_device(device_id, limit)

    if metrics is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )

    return metrics
