"""연결 요청, 수락, 거절, 연결 해제 서비스를 정의한다."""

from app.domain.connection import ConnectionRequest, GuardianProtectedConnection
from app.repository.connection_repository import ConnectionRepository
from app.repository.user_repository import UserRepository
from app.service.notification_service import NotificationService


class ConnectionService:
    """연결 아이디 기반 연결 요청, 수락, 해제를 처리한다."""

    def __init__(
        self,
        user_repository: UserRepository,
        connection_repository: ConnectionRepository,
        notification_service: NotificationService,
    ) -> None:
        self.user_repository = user_repository
        self.connection_repository = connection_repository
        self.notification_service = notification_service

    def request_connection(self, requester_user_id: str, target_connection_code: str) -> ConnectionRequest:
        """서로 다른 역할인지 확인한 뒤 상대방의 연결 아이디로 연결 요청을 생성한다."""
        raise NotImplementedError

    def accept_connection_request(self, request_id: str, responder_user_id: str) -> GuardianProtectedConnection:
        """보호대상자에게 활성 보호자가 없는지 확인한 뒤 연결 요청을 수락한다."""
        raise NotImplementedError

    def reject_connection_request(self, request_id: str, responder_user_id: str) -> ConnectionRequest:
        """연결 요청을 거절 상태로 변경한다."""
        raise NotImplementedError

    def disconnect(self, connection_id: str, requested_by_user_id: str) -> None:
        """연결을 해제하고 해당 연결과 관련된 기록을 삭제한다."""
        raise NotImplementedError
