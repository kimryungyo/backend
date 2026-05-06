"""알림 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.domain.notification import NotificationMessage


class NotificationRepository(ABC):
    """전송할 알림과 전송 결과를 저장한다."""

    @abstractmethod
    def save(self, message: NotificationMessage) -> None:
        """알림 메시지와 전송 상태를 저장한다."""
        raise NotImplementedError
