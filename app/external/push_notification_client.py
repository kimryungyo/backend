"""푸시 알림 서비스 연동 클라이언트를 정의한다."""

from app.domain.notification import NotificationMessage


class PushNotificationClient:
    """외부 푸시 알림 서비스로 알림 전송을 요청한다."""

    def send(self, message: NotificationMessage) -> None:
        """알림 메시지를 대상 사용자의 기기로 전송한다."""
        raise NotImplementedError
