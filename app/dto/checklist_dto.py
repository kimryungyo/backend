"""재난 체크리스트 조회와 수행 기록 DTO를 정의한다."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import ProtectedCategory


class ChecklistRuleResponse(BaseModel):
    """재난 상황에서 제공할 체크리스트 규칙을 반환한다."""

    rule_id: str
    disaster_type: str
    category: ProtectedCategory
    title: str
    interval_minutes: int
    enabled: bool


class ChecklistCompleteRequest(BaseModel):
    """보호대상자가 완료한 체크리스트 항목 정보를 수신한다."""

    disaster_event_id: str = Field(..., description="진행 중인 재난 상황 ID")
    checklist_rule_id: str = Field(..., description="완료한 체크리스트 규칙 ID")
    completed_at: datetime | None = Field(default=None, description="클라이언트 기준 완료 시각")


class ChecklistRecordResponse(BaseModel):
    """체크리스트 수행 기록을 반환한다."""

    record_id: str
    protected_user_id: str
    disaster_event_id: str
    checklist_rule_id: str
    completed_at: datetime
