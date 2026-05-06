"""카카오 로그인 및 사용자 생성 API를 담당한다."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_auth_service
from app.dto.auth_dto import KakaoLoginRequest, LoginResponse
from app.service.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/kakao-login", response_model=LoginResponse)
def kakao_login(payload: KakaoLoginRequest, service: AuthService = Depends(get_auth_service)) -> LoginResponse:
    """카카오 access token으로 로그인하거나 역할이 고정된 사용자를 생성한다."""
    raise NotImplementedError
