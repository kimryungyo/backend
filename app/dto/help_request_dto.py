"""도움 요청 DTO를 정의한다."""

from datetime import datetime

from pydantic import BaseModel


class HelpRequestCreate(BaseModel):
    """보호대상자의 도움 요청 입력을 수신한다."""

    requested_at: datetime | None = None


class HelpRequestResponse(BaseModel):
    """도움 요청 생성 결과를 반환한다."""

    request_id: str
    protected_user_id: str
    guardian_user_id: str
    location_share_id: str
    requested_at: datetime
