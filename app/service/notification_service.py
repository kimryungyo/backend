"""서비스 이벤트를 푸시 알림으로 변환하고 전송하는 서비스를 정의한다."""

from app.domain.connection import ConnectionRequest
from app.domain.help_request import HelpRequestRecord
from app.domain.location import LocationRequest
from app.domain.notification import NotificationMessage
from app.external.push_notification_client import PushNotificationClient
from app.repository.notification_repository import NotificationRepository


class NotificationService:
    """서비스 내부 이벤트를 사용자에게 보낼 푸시 알림으로 변환한다."""

    def __init__(self, notification_repository: NotificationRepository, push_client: PushNotificationClient) -> None:
        self.notification_repository = notification_repository
        self.push_client = push_client

    def notify(self, message: NotificationMessage) -> None:
        """알림 메시지를 저장한 뒤 푸시 알림 서비스로 전송한다."""
        raise NotImplementedError

    def notify_connection_request(self, request: ConnectionRequest) -> None:
        """연결 요청을 받은 사용자에게 알림을 보낸다."""
        raise NotImplementedError

    def notify_safety_nonresponse(self, protected_user_id: str, guardian_user_id: str) -> None:
        """정기 안부 미응답 상태를 보호자에게 알린다."""
        raise NotImplementedError

    def notify_help_request(self, help_request: HelpRequestRecord) -> None:
        """보호대상자의 도움 요청을 보호자에게 알린다."""
        raise NotImplementedError

    def notify_location_request(self, location_request: LocationRequest) -> None:
        """보호자의 위치 요청을 보호대상자에게 알린다."""
        raise NotImplementedError
