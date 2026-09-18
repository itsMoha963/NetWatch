from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert import Alert, AlertType


class AlertRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_unresolved(
        self,
        device_id: int,
        alert_type: AlertType,
    ) -> Alert | None:
        statement = select(Alert).where(
            Alert.device_id == device_id,
            Alert.alert_type == alert_type,
            Alert.resolved.is_(False),
        )
        return self._session.scalar(statement)

    def create(self, alert: Alert) -> Alert:
        self._session.add(alert)
        self._session.commit()
        self._session.refresh(alert)
        return alert

    def save(self, alert: Alert) -> Alert:
        self._session.commit()
        self._session.refresh(alert)
        return alert

    def list_all(
        self,
        resolved: bool | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        statement = select(Alert).order_by(Alert.created_at.desc(), Alert.id.desc())

        if resolved is not None:
            statement = statement.where(Alert.resolved == resolved)

        statement = statement.limit(limit)
        return list(self._session.scalars(statement))

    def list_for_device(
        self,
        device_id: int,
        resolved: bool | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        statement = select(Alert).where(Alert.device_id == device_id)

        if resolved is not None:
            statement = statement.where(Alert.resolved == resolved)

        statement = statement.order_by(
            Alert.created_at.desc(),
            Alert.id.desc(),
        ).limit(limit)
        return list(self._session.scalars(statement))

    def resolve(self, alert: Alert, resolved_at: datetime | None = None) -> Alert:
        alert.resolved = True
        alert.resolved_at = resolved_at or datetime.now(UTC)
        return self.save(alert)
