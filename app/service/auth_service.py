"""카카오 로그인과 역할 고정 사용자 생성을 처리하는 서비스를 정의한다."""

import secrets
import string
import uuid
from datetime import datetime, timezone

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
        user_info = self.kakao_client.verify_token(access_token)
        kakao_id = str(user_info["id"])

        user = self.user_repository.find_by_kakao_id(kakao_id)
        if user:
            return user

        # 신규 사용자 생성
        user_id = uuid.uuid4().hex
        nickname = user_info.get("properties", {}).get("nickname", "사용자")
        connection_code = self._generate_unique_connection_code()

        new_user = User(
            user_id=user_id,
            kakao_id=kakao_id,
            role=initial_role,
            connection_code=connection_code,
            name=nickname,
            created_at=datetime.now(timezone.utc),
        )
        self.user_repository.save(new_user)
        return new_user

    def _generate_unique_connection_code(self) -> str:
        """중복되지 않는 6자리의 영문 대문자 및 숫자 조합 코드를 생성한다."""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = "".join(secrets.choice(chars) for _ in range(6))
            if not self.user_repository.find_by_connection_code(code):
                return code
