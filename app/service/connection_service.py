"""연결 요청, 수락, 거절, 연결 해제 서비스를 정의한다."""

import uuid
from datetime import datetime, timezone

from app.domain.connection import ConnectionRequest, GuardianProtectedConnection
from app.domain.enums import ConnectionRequestStatus
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
        requester = self.user_repository.find_by_id(requester_user_id)
        if not requester:
            raise ValueError(f"requester not found: {requester_user_id}")

        target = self.user_repository.find_by_connection_code(target_connection_code)
        if not target:
            raise ValueError(f"target user not found with code: {target_connection_code}")

        if not requester.can_request_connection_to(target):
            raise ValueError("cannot request connection to self or user with same role")

        # 기존 연결 확인 (보호대상자는 1명만 연결 가능, 보호자는 여러 명 가능하지만 중복 요청 방지)
        if requester.is_protected():
            if self.connection_repository.find_active_by_protected(requester_user_id):
                raise ValueError("protected user already has an active connection")
        
        if target.is_protected():
            if self.connection_repository.find_active_by_protected(target.user_id):
                raise ValueError("target protected user already has an active connection")

        request = ConnectionRequest(
            request_id=uuid.uuid4().hex,
            requester_user_id=requester_user_id,
            target_user_id=target.user_id,
            status=ConnectionRequestStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        self.connection_repository.save_request(request)
        self.notification_service.notify_connection_request(request)
        
        return request

    def accept_connection_request(self, request_id: str, responder_user_id: str) -> GuardianProtectedConnection:
        """보호대상자에게 활성 보호자가 없는지 확인한 뒤 연결 요청을 수락한다."""
        request = self.connection_repository.get_request(request_id)
        if not request:
            raise ValueError(f"connection request not found: {request_id}")

        if not request.can_be_responded_by(responder_user_id):
            raise ValueError("invalid responder or request is not pending")

        requester = self.user_repository.find_by_id(request.requester_user_id)
        responder = self.user_repository.find_by_id(responder_user_id)

        if not requester or not responder:
            raise ValueError("requester or responder not found")

        # 보호대상자 확인 및 기존 연결 체크
        protected_user_id = (
            request.requester_user_id if requester.is_protected() else responder_user_id
        )
        guardian_user_id = (
            responder_user_id if requester.is_protected() else request.requester_user_id
        )

        if self.connection_repository.find_active_by_protected(protected_user_id):
            raise ValueError("protected user already has an active connection")

        # 요청 수락 처리
        now = datetime.now(timezone.utc)
        request.accept(now)
        self.connection_repository.save_request(request)

        # 활성 연결 생성
        connection = GuardianProtectedConnection(
            connection_id=uuid.uuid4().hex,
            guardian_user_id=guardian_user_id,
            protected_user_id=protected_user_id,
            created_at=now,
        )
        self.connection_repository.save_connection(connection)

        return connection

    def reject_connection_request(self, request_id: str, responder_user_id: str) -> ConnectionRequest:
        """연결 요청을 거절 상태로 변경한다."""
        request = self.connection_repository.get_request(request_id)
        if not request:
            raise ValueError(f"connection request not found: {request_id}")

        if not request.can_be_responded_by(responder_user_id):
            raise ValueError("invalid responder or request is not pending")

        # 요청 거절 처리
        request.reject(datetime.now(timezone.utc))
        self.connection_repository.save_request(request)

        return request

    def disconnect(self, connection_id: str, requested_by_user_id: str) -> None:
        """연결을 해제하고 해당 연결과 관련된 기록을 삭제한다."""
        try:
            connection = self.connection_repository.get_connection(connection_id)
        except KeyError as exc:
            raise ValueError(f"active connection not found: {connection_id}") from exc

        if not connection.involves_user(requested_by_user_id):
            raise PermissionError("requester is not a connection participant")

        self.connection_repository.delete_connection_and_related_records(connection_id)
