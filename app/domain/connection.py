"""보호자와 보호대상자의 연결 도메인 모델을 정의한다."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import ConnectionRequestStatus


@dataclass
class ConnectionRequest:
    """한 사용자가 상대방의 연결 아이디로 보낸 연결 요청을 나타낸다."""

    request_id: str  # 연결 요청 ID
    requester_user_id: str  # 연결 요청을 보낸 사용자 ID
    target_user_id: str  # 연결 요청을 받은 사용자 ID
    status: ConnectionRequestStatus  # 요청 수락, 거절, 취소 상태
    created_at: datetime  # 연결 요청 생성 시각
    responded_at: datetime | None = None  # 상대방이 요청에 응답한 시각

    def is_pending(self) -> bool:
        """연결 요청이 아직 응답 대기 상태인지 확인한다."""
        return self.status == ConnectionRequestStatus.PENDING

    def can_be_responded_by(self, user_id: str) -> bool:
        """지정한 사용자가 이 연결 요청에 응답할 수 있는지 확인한다."""
        return self.target_user_id == user_id and self.is_pending()

    def accept(self, responded_at: datetime) -> None:
        """연결 요청을 수락 상태로 변경한다."""
        self.status = ConnectionRequestStatus.ACCEPTED
        self.responded_at = responded_at

    def reject(self, responded_at: datetime) -> None:
        """연결 요청을 거절 상태로 변경한다."""
        self.status = ConnectionRequestStatus.REJECTED
        self.responded_at = responded_at

    def cancel(self, responded_at: datetime) -> None:
        """연결 요청을 취소 상태로 변경한다."""
        self.status = ConnectionRequestStatus.CANCELED
        self.responded_at = responded_at


@dataclass
class GuardianProtectedConnection:
    """보호자와 보호대상자의 활성 연결 관계를 나타낸다."""

    connection_id: str  # 보호자-보호대상자 연결 ID
    guardian_user_id: str  # 보호자 사용자 ID
    protected_user_id: str  # 보호대상자 사용자 ID
    created_at: datetime  # 연결이 생성된 시각

    def involves_user(self, user_id: str) -> bool:
        """지정한 사용자가 이 연결에 포함되어 있는지 확인한다."""
        return user_id in {self.guardian_user_id, self.protected_user_id}

    def connects(self, guardian_user_id: str, protected_user_id: str) -> bool:
        """지정한 보호자와 보호대상자 쌍의 연결인지 확인한다."""
        return self.guardian_user_id == guardian_user_id and self.protected_user_id == protected_user_id
