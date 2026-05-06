"""위치 요청과 위치 공유 DTO를 정의한다."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import LocationRequestStatus


class LocationRequestCreate(BaseModel):
    """보호자가 보호대상자에게 위치 요청을 보낼 때의 입력을 수신한다."""

    protected_user_id: str = Field(..., description="위치 요청 대상 보호대상자 ID")


class LocationRequestResponse(BaseModel):
    """위치 요청 상태를 반환한다."""

    request_id: str
    guardian_user_id: str
    protected_user_id: str
    status: LocationRequestStatus
    requested_at: datetime
    expires_at: datetime


class GeoLocationResponse(BaseModel):
    """보호자에게 공유된 위치 좌표와 표시 정보를 반환한다."""

    latitude: float
    longitude: float
    accuracy_meters: float | None
    address: str | None
    captured_at: datetime


class LocationShareResponse(BaseModel):
    """위치 공유 결과를 반환한다."""

    share_id: str
    guardian_user_id: str
    protected_user_id: str
    location: GeoLocationResponse
    reason: str
    shared_at: datetime
