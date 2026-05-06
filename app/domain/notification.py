"""푸시 알림 도메인 모델을 정의한다."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import NotificationType


@dataclass
class NotificationMessage:
    """푸시 알림으로 전송할 메시지를 나타낸다."""

    notification_id: str  # 알림 ID
    receiver_user_id: str  # 알림을 받을 사용자 ID
    notification_type: NotificationType  # 알림 종류
    title: str  # 알림 제목
    body: str  # 알림 본문
    created_at: datetime  # 알림 생성 시각
    sent_at: datetime | None = None  # 알림 전송 완료 시각

    def is_for_user(self, user_id: str) -> bool:
        """알림 수신자가 지정한 사용자인지 확인한다."""
        return self.receiver_user_id == user_id

    def is_sent(self) -> bool:
        """알림이 전송 완료 상태인지 확인한다."""
        return self.sent_at is not None

    def mark_sent(self, sent_at: datetime) -> None:
        """알림을 전송 완료 상태로 표시한다."""
        self.sent_at = sent_at
