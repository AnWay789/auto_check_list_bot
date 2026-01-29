"""Pydantic модели для проверки дашбордов."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel


class DashboardInfo(BaseModel):
    """Информация о дашборде для проверки (входные данные от Django)."""

    event_uuid: str
    dashboard_uid: str
    name: str
    description: str | None = None
    real_url: str
    fake_url: str
    time_for_check: int  # минуты


class DashboardCheck(BaseModel):
    """Внутренняя модель для отслеживания состояния проверки."""

    event_uuid: str
    dashboard_uid: str
    name: str
    description: str | None = None
    real_url: str
    fake_url: str
    time_for_check: int

    message_id: Optional[int] = None
    sent_at: datetime
    expires_at: datetime

    link_clicked: bool = False
    button_clicked: bool = False
    problem: Optional[bool] = None

    @classmethod
    def from_dashboard_info(cls, info: DashboardInfo) -> "DashboardCheck":
        now = datetime.now()
        expires_at = now + timedelta(minutes=info.time_for_check)
        return cls(
            event_uuid=info.event_uuid,
            dashboard_uid=info.dashboard_uid,
            name=info.name,
            description=info.description,
            real_url=info.real_url,
            fake_url=info.fake_url,
            time_for_check=info.time_for_check,
            sent_at=now,
            expires_at=expires_at,
        )

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

