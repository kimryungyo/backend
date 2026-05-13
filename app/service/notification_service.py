"""서비스 이벤트를 푸시 알림으로 변환하고 전송하는 서비스를 정의한다."""

from datetime import datetime, timezone
import uuid

from app.domain.connection import ConnectionRequest
from app.domain.enums import NotificationType
from app.domain.help_request import HelpRequestRecord
from app.domain.location import LocationRequest
from app.domain.notification import NotificationMessage
from app.external.push_notification_client import PushNotificationClient
from app.repository.notification_repository import NotificationRepository
from app.repository.user_repository import UserRepository


class NotificationService:
    """서비스 내부 이벤트를 사용자에게 보낼 푸시 알림으로 변환한다."""

    def __init__(
        self,
        notification_repository: NotificationRepository,
        user_repository: UserRepository,
        push_client: PushNotificationClient,
    ) -> None:
        self.notification_repository = notification_repository
        self.user_repository = user_repository
        self.push_client = push_client

    def notify(self, message: NotificationMessage) -> None:
        """알림 메시지를 저장한 뒤 푸시 알림 서비스로 전송한다."""
        self.notification_repository.save(message)
        self.push_client.send(message)
        message.mark_sent(datetime.now(timezone.utc))
        self.notification_repository.save(message)

    def notify_connection_request(self, request: ConnectionRequest) -> None:
        """연결 요청을 받은 사용자에게 알림을 보낸다."""
        requester = self.user_repository.find_by_id(request.requester_user_id)
        requester_name = requester.name if requester else "알 수 없는 사용자"

        message = NotificationMessage(
            notification_id=uuid.uuid4().hex,
            receiver_user_id=request.target_user_id,
            notification_type=NotificationType.CONNECTION_REQUEST,
            title=f"{requester_name}님의 연결 요청",
            body=f"{requester_name}님이 연결을 요청했습니다. 앱에서 확인 후 수락해 주세요.",
            created_at=datetime.now(timezone.utc),
        )
        self.notify(message)

    def notify_safety_nonresponse(self, protected_user_id: str, guardian_user_id: str) -> None:
        """정기 안부 미응답 상태를 보호자에게 알린다."""
        protected = self.user_repository.find_by_id(protected_user_id)
        protected_name = protected.name if protected else "보호대상자"

        message = NotificationMessage(
            notification_id=uuid.uuid4().hex,
            receiver_user_id=guardian_user_id,
            notification_type=NotificationType.SAFETY_NOT_RESPONDED,
            title="안부 확인 미응답 알림",
            body=f"{protected_name}님이 정기 안부 확인에 응답하지 않았습니다. 확인이 필요합니다.",
            created_at=datetime.now(timezone.utc),
        )
        self.notify(message)

    def notify_help_request(self, help_request: HelpRequestRecord) -> None:
        """보호대상자의 도움 요청을 보호자에게 알린다."""
        protected = self.user_repository.find_by_id(help_request.protected_user_id)
        protected_name = protected.name if protected else "보호대상자"

        message = NotificationMessage(
            notification_id=uuid.uuid4().hex,
            receiver_user_id=help_request.guardian_user_id,
            notification_type=NotificationType.HELP_REQUEST,
            title="🚨 긴급 도움 요청",
            body=f"{protected_name}님이 도움을 요청했습니다! 현재 위치를 확인하세요.",
            created_at=datetime.now(timezone.utc),
        )
        self.notify(message)

    def notify_location_request(self, location_request: LocationRequest) -> None:
        """보호자의 위치 요청을 보호대상자에게 알린다."""
        guardian = self.user_repository.find_by_id(location_request.guardian_user_id)
        guardian_name = guardian.name if guardian else "보호자"

        message = NotificationMessage(
            notification_id=uuid.uuid4().hex,
            receiver_user_id=location_request.protected_user_id,
            notification_type=NotificationType.LOCATION_REQUEST,
            title="위치 공유 요청",
            body=f"{guardian_name}님이 현재 위치를 요청했습니다.",
            created_at=datetime.now(timezone.utc),
        )
        self.notify(message)
