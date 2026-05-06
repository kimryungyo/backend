"""보호자와 보호대상자 프로필 DTO를 정의한다."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import ProtectedCategory


class ProtectedProfileUpdateRequest(BaseModel):
    """보호대상자의 재난 대응 특성 분류와 지역 정보를 수신한다."""

    categories: list[ProtectedCategory] = Field(..., description="1차 보호대상자 분류 목록")
    region_code: str = Field(..., description="재난 정보 매칭에 사용할 지역 코드")


class AutoLocationShareUpdateRequest(BaseModel):
    """위치 요청 미응답 시 자동 공유 설정 변경 값을 수신한다."""

    enabled: bool = Field(..., description="자동 위치 공유 허용 여부")


class ProtectedProfileResponse(BaseModel):
    """보호대상자 프로필 조회 또는 수정 결과를 반환한다."""

    user_id: str
    categories: list[ProtectedCategory]
    region_code: str
    auto_location_share_enabled: bool
    updated_at: datetime


class GuardianProfileResponse(BaseModel):
    """보호자 프로필 조회 결과를 반환한다."""

    user_id: str
    phone_number: str | None
    updated_at: datetime
