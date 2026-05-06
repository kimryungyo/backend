"""도움 요청과 도움 요청 시 위치 공유 서비스를 정의한다."""

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
        raise NotImplementedError
