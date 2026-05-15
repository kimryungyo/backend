"""알림 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.database.mysql import MySQLPool
from app.domain.notification import NotificationMessage


class NotificationRepository(ABC):
    """전송할 알림과 전송 결과를 저장한다."""

    @abstractmethod
    def save(self, message: NotificationMessage) -> None:
        """알림 메시지와 전송 상태를 저장한다."""
        raise NotImplementedError


class MySQLNotificationRepository(NotificationRepository):
    """MySQL 기반 알림 repository 구현체."""

    def __init__(self, mysql_pool: MySQLPool) -> None:
        self._pool = mysql_pool

    def save(self, message: NotificationMessage) -> None:
        """알림 메시지와 전송 상태를 저장한다."""
        sql = """
            INSERT INTO notifications
                (notification_id, receiver_user_id, notification_type, title, body, created_at, sent_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                sent_at = VALUES(sent_at)
        """
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (
                    message.notification_id,
                    message.receiver_user_id,
                    message.notification_type.value,
                    message.title,
                    message.body,
                    message.created_at,
                    message.sent_at,
                ))
            finally:
                cursor.close()
