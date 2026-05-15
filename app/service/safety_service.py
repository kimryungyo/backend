"""안부 확인 기록과 정기 안부 미응답 판단 서비스를 정의한다."""

import uuid
from datetime import datetime, time, timezone

from app.domain.enums import NotificationType, SafetyStatus
from app.domain.safety import SafetyCheckRecord, SafetySchedule
from app.repository.connection_repository import ConnectionRepository
from app.repository.safety_repository import SafetyRepository
from app.repository.user_repository import UserRepository
from app.service.notification_service import NotificationService


class SafetyCheckService:
    """평상시 정기 안부 확인과 안부 미응답 판단을 담당한다."""

    def __init__(
        self,
        safety_repository: SafetyRepository,
        connection_repository: ConnectionRepository,
        user_repository: UserRepository,
        notification_service: NotificationService,
    ) -> None:
        self.safety_repository = safety_repository
        self.connection_repository = connection_repository
        self.user_repository = user_repository
        self.notification_service = notification_service

    def configure_schedule(
        self,
        guardian_user_id: str,
        protected_user_id: str,
        enabled: bool,
        check_times: list[time],
        grace_minutes: int,
    ) -> SafetySchedule:
        """보호자가 보호대상자의 정기 안부 시간대와 여유시간을 설정한다."""
        # 1. 활성 연결 관계 확인
        connection = self.connection_repository.find_active_by_protected(protected_user_id)
        if not connection or connection.guardian_user_id != guardian_user_id:
            raise ValueError(
                f"Active connection not found between guardian {guardian_user_id} "
                f"and protected user {protected_user_id}"
            )

        # 2. 기존 설정 조회 또는 신규 생성
        schedule = self.safety_repository.get_schedule(protected_user_id)
        now = datetime.now(timezone.utc)

        if schedule:
            schedule.enabled = enabled
            schedule.check_times = check_times
            schedule.grace_minutes = grace_minutes
            schedule.updated_at = now
        else:
            schedule = SafetySchedule(
                schedule_id=uuid.uuid4().hex,
                guardian_user_id=guardian_user_id,
                protected_user_id=protected_user_id,
                enabled=enabled,
                check_times=check_times,
                grace_minutes=grace_minutes,
                updated_at=now,
            )

        # 3. 저장 및 반환
        self.safety_repository.save_schedule(schedule)
        return schedule

    def record_safety_check(self, protected_user_id: str, checked_at: datetime | None) -> SafetyCheckRecord:
        """보호대상자의 안부 확인 입력을 기록한다."""
        # 1. 사용자 존재 및 역할 확인
        user = self.user_repository.find_by_id(protected_user_id)
        if not user:
            raise ValueError(f"User not found: {protected_user_id}")
        if not user.is_protected():
            raise ValueError(f"User {protected_user_id} is not a protected user")

        # 2. 기록 생성
        record = SafetyCheckRecord(
            record_id=uuid.uuid4().hex,
            protected_user_id=protected_user_id,
            status=SafetyStatus.SAFE,
            checked_at=checked_at or datetime.now(timezone.utc),
        )

        # 3. 저장 및 반환
        self.safety_repository.save_check_record(record)
        return record

    def detect_nonresponse(self, protected_user_id: str, now: datetime) -> bool:
        """보호자가 설정한 시간대와 여유시간 기준으로 미응답 여부를 판단하고 알림을 발송한다."""
        # 1. 안부 확인 설정 조회 및 활성 여부 확인
        schedule = self.safety_repository.get_schedule(protected_user_id)
        if not schedule or not schedule.is_active():
            return False

        # 2. 최근 안부 확인 기록 조회
        latest_record = self.safety_repository.get_latest_check_record(protected_user_id)
        latest_check_at = latest_record.checked_at if latest_record else None

        # 3. 도메인 로직에 위임하여 미응답 여부 판단
        is_unresponsive = schedule.is_late_after_window(latest_check_at, now)

        if is_unresponsive:
            # 4. 미응답 시 보호자에게 알림 발송
            connection = self.connection_repository.find_active_by_protected(protected_user_id)
            if connection:
                self.notification_service.send_notification(
                    user_id=connection.guardian_user_id,
                    notification_type=NotificationType.SAFETY_NOT_RESPONDED,
                    title="안부 미응답 알림",
                    content="보호대상자가 설정된 시간에 안부를 확인하지 않았습니다. 확인이 필요합니다.",
                    related_id=protected_user_id,
                )

        return is_unresponsive
