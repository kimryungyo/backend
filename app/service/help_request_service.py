"""도움 요청과 도움 요청 시 위치 공유 서비스를 정의한다."""

import uuid
from datetime import datetime

from app.domain.help_request import HelpRequestRecord
from app.repository.connection_repository import ConnectionRepository
from app.service.location_service import LocationShareService
from app.service.notification_service import NotificationService


class HelpRequestService:
    """보호대상자의 도움 요청을 기록하고 보호자에게 알림을 보낸다."""

    def __init__(
        self,
        connection_repository: ConnectionRepository,
        location_share_service: LocationShareService,
        notification_service: NotificationService,
    ) -> None:
        self.connection_repository = connection_repository
        self.location_share_service = location_share_service
        self.notification_service = notification_service

    def request_help(self, protected_user_id: str, requested_at: datetime) -> HelpRequestRecord:
        """보호대상자의 도움 요청을 생성하고 위치 공유와 보호자 알림을 함께 처리한다."""
        # 1. 활성 연결 확인
        connection = self.connection_repository.find_active_by_protected(protected_user_id)
        if not connection:
            raise ValueError(f"No active connection found for protected user: {protected_user_id}")

        # 2. 도움 요청용 위치 공유 기록 생성
        share_record = self.location_share_service.share_for_help_request(
            guardian_user_id=connection.guardian_user_id,
            protected_user_id=protected_user_id,
        )

        # 3. 도움 요청 기록 생성
        record = HelpRequestRecord(
            request_id=uuid.uuid4().hex,
            protected_user_id=protected_user_id,
            guardian_user_id=connection.guardian_user_id,
            location_share_id=share_record.share_id,
            requested_at=requested_at,
        )

        # 4. 보호자에게 알림 전송
        self.notification_service.notify_help_request(record)

        return record
