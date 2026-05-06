"""사용자 계정 도메인 모델을 정의한다."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import UserRole


@dataclass
class User:
    """카카오 로그인 후 생성되는 기본 사용자 계정을 나타낸다."""

    user_id: str  # 시스템 내부 사용자 ID
    kakao_id: str  # 카카오 OAuth에서 제공하는 사용자 식별자
    role: UserRole  # 1차에서는 가입 후 변경할 수 없는 사용자 역할
    connection_code: str  # 상대방이 연결 요청에 사용하는 6자리 고유 연결 아이디
    name: str  # 서비스 화면과 알림에 표시할 이름
    created_at: datetime  # 사용자 계정 생성 시각

    def is_guardian(self) -> bool:
        """사용자가 보호자 역할인지 확인한다."""
        return self.role == UserRole.GUARDIAN

    def is_protected(self) -> bool:
        """사용자가 보호대상자 역할인지 확인한다."""
        return self.role == UserRole.PROTECTED

    def can_request_connection_to(self, target: "User") -> bool:
        """서로 다른 역할의 사용자에게만 연결 요청을 보낼 수 있는지 확인한다."""
        return self.user_id != target.user_id and self.role != target.role
