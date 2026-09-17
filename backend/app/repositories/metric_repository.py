from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.metric import Metric


class MetricRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, metric: Metric) -> Metric:
        self._session.add(metric)
        self._session.commit()
        self._session.refresh(metric)
        return metric

    def list_for_device(
        self,
        device_id: int,
        limit: int = 100,
    ) -> list[Metric]:
        statement = (
            select(Metric)
            .where(Metric.device_id == device_id)
            .order_by(Metric.recorded_at.desc(), Metric.id.desc())
            .limit(limit)
        )

        return list(self._session.scalars(statement))
