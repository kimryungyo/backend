"""재난 정보와 재난 카탈로그 DTO를 정의한다."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DisasterEventResponse(BaseModel):
    """현재 적용 중인 재난 상황 정보를 반환한다."""

    event_id: str
    disaster_type: str
    region_code: str
    alert_level: str
    started_at: datetime
    ended_at: datetime | None = None


class DisasterCatalogResponse(BaseModel):
    """JSON 기반 재난 카탈로그 정보를 반환한다."""

    version: str
    updated_at: datetime
    disasters: list[dict[str, Any]] = Field(default_factory=list)
