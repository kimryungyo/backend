"""안부 확인과 정기 안부 설정 DTO를 정의한다."""

from datetime import datetime, time

from pydantic import BaseModel, Field

from app.domain.enums import SafetyStatus


class SafetyScheduleUpdateRequest(BaseModel):
    """보호자가 설정하는 정기 안부 시간대와 여유시간을 수신한다."""

    protected_user_id: str = Field(..., description="정기 안부 확인 대상 보호대상자 ID")
    enabled: bool = Field(..., description="정기 안부 확인 사용 여부")
    check_times: list[time] = Field(default_factory=list, description="안부 확인 시간대 목록")
    grace_minutes: int = Field(default=120, ge=0, description="각 시간대 앞뒤 허용 시간")


class SafetyCheckCreate(BaseModel):
    """보호대상자의 안부 확인 입력을 수신한다."""

    checked_at: datetime | None = Field(default=None, description="클라이언트 기준 안부 확인 시각")


class SafetyScheduleResponse(BaseModel):
    """정기 안부 확인 설정을 반환한다."""

    schedule_id: str
    guardian_user_id: str
    protected_user_id: str
    enabled: bool
    check_times: list[time]
    grace_minutes: int
    updated_at: datetime


class SafetyCheckResponse(BaseModel):
    """안부 확인 기록을 반환한다."""

    record_id: str
    protected_user_id: str
    status: SafetyStatus
    checked_at: datetime
