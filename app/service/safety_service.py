"""안부 확인 기록과 정기 안부 미응답 판단 서비스를 정의한다."""

from datetime import datetime

from app.domain.safety import SafetyCheckRecord, SafetySchedule
from app.repository.connection_repository import ConnectionRepository
from app.repository.safety_repository import SafetyRepository
from app.service.notification_service import NotificationService


class SafetyCheckService:
    """평상시 정기 안부 확인과 안부 미응답 판단을 담당한다."""

    def __init__(
        self,
        safety_repository: SafetyRepository,
        connection_repository: ConnectionRepository,
        notification_service: NotificationService,
    ) -> None:
        self.safety_repository = safety_repository
        self.connection_repository = connection_repository
        self.notification_service = notification_service

    def configure_schedule(self, schedule: SafetySchedule) -> SafetySchedule:
        """보호자가 보호대상자의 정기 안부 시간대와 여유시간을 설정한다."""
        raise NotImplementedError

    def record_safety_check(self, protected_user_id: str, checked_at: datetime) -> SafetyCheckRecord:
        """보호대상자의 안부 확인 입력을 기록한다."""
        raise NotImplementedError

    def detect_nonresponse(self, protected_user_id: str, now: datetime) -> bool:
        """보호자가 설정한 시간대와 여유시간 기준으로 미응답 여부를 판단한다."""
        raise NotImplementedError
