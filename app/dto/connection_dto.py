"""보호자와 보호대상자 연결 DTO를 정의한다."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import ConnectionRequestStatus


class ConnectionRequestCreate(BaseModel):
    """상대방의 연결 아이디로 연결 요청을 생성하는 입력을 수신한다."""

    target_connection_code: str = Field(..., min_length=6, max_length=6, description="상대방의 6자리 연결 아이디")


class ConnectionRequestResponse(BaseModel):
    """연결 요청 상태를 반환한다."""

    request_id: str
    requester_user_id: str
    target_user_id: str
    status: ConnectionRequestStatus
    created_at: datetime
    responded_at: datetime | None = None


class ConnectionResponse(BaseModel):
    """활성 보호자-보호대상자 연결 정보를 반환한다."""

    connection_id: str
    guardian_user_id: str
    protected_user_id: str
    created_at: datetime
