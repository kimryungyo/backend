"""로그인 요청과 응답 DTO를 정의한다."""

from pydantic import BaseModel, Field

from app.domain.enums import UserRole


class KakaoLoginRequest(BaseModel):
    """카카오 access token과 최초 가입 역할을 수신한다."""

    access_token: str = Field(..., description="카카오 OAuth access token")
    initial_role: UserRole = Field(..., description="가입 시 고정되는 사용자 역할")


class LoginResponse(BaseModel):
    """로그인 또는 가입 완료 후 클라이언트에 반환할 사용자 정보를 나타낸다."""

    user_id: str = Field(..., description="시스템 내부 사용자 ID")
    role: UserRole = Field(..., description="사용자 역할")
    connection_code: str = Field(..., description="6자리 고유 연결 아이디")
    name: str = Field(..., description="화면 표시 이름")
