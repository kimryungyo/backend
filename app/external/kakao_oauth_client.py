"""카카오 OAuth 연동 클라이언트를 정의한다."""

from typing import Any


class KakaoOAuthClient:
    """카카오 OAuth 서비스와의 인증 연동을 담당한다."""

    def verify_token(self, access_token: str) -> dict[str, Any]:
        """카카오 access token을 검증하고 사용자 식별 정보를 반환한다."""
        raise NotImplementedError
