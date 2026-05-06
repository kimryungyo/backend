"""카카오 로그인과 역할 고정 사용자 생성을 처리하는 서비스를 정의한다."""

from app.domain.enums import UserRole
from app.domain.user import User
from app.external.kakao_oauth_client import KakaoOAuthClient
from app.repository.user_repository import UserRepository


class AuthService:
    """카카오 로그인 결과를 재난안심 사용자 계정으로 연결한다."""

    def __init__(self, kakao_client: KakaoOAuthClient, user_repository: UserRepository) -> None:
        self.kakao_client = kakao_client
        self.user_repository = user_repository

    def login_or_register(self, access_token: str, initial_role: UserRole) -> User:
        """카카오 인증 후 기존 사용자를 로그인시키거나 역할이 고정된 신규 사용자를 생성한다."""
        raise NotImplementedError
