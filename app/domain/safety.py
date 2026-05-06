"""안부 확인 설정과 기록 도메인 모델을 정의한다."""

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from app.domain.enums import SafetyStatus


@dataclass
class SafetySchedule:
    """보호자가 설정하는 평상시 정기 안부 확인 규칙을 나타낸다."""

    schedule_id: str  # 안부 확인 설정 ID
    guardian_user_id: str  # 설정을 관리하는 보호자 사용자 ID
    protected_user_id: str  # 안부 확인 대상 보호대상자 사용자 ID
    enabled: bool  # 정기 안부 확인 사용 여부
    check_times: list[time]  # 안부 확인을 기대하는 하루 중 시간 목록
    grace_minutes: int  # 각 시간대 앞뒤로 허용되는 여유 시간
    updated_at: datetime  # 설정이 마지막으로 변경된 시각

    def is_active(self) -> bool:
        """정기 안부 확인 규칙이 실제로 활성 상태인지 확인한다."""
        return self.enabled and bool(self.check_times)

    def is_in_check_window(self, now: datetime) -> bool:
        """현재 시각이 설정된 안부 확인 허용 시간대 안에 있는지 확인한다."""
        if not self.is_active():
            return False

        grace = timedelta(minutes=self.grace_minutes)
        for check_time in self.check_times:
            for day_offset in (-1, 0, 1):
                target_date = now.date() + timedelta(days=day_offset)
                target = datetime.combine(target_date, check_time, tzinfo=now.tzinfo)
                if abs(now - target) <= grace:
                    return True
        return False

    def is_late_after_window(self, latest_check_at: datetime | None, now: datetime) -> bool:
        """가장 최근 안부 확인 시각을 기준으로 현재 미응답 상태인지 판단한다."""
        if not self.is_active():
            return False

        grace = timedelta(minutes=self.grace_minutes)
        for check_time in self.check_times:
            for day_offset in (-1, 0):
                target_date = now.date() + timedelta(days=day_offset)
                target = datetime.combine(target_date, check_time, tzinfo=now.tzinfo)
                window_start = target - grace
                window_end = target + grace

                if now <= window_end:
                    continue
                if latest_check_at is None or not window_start <= latest_check_at <= window_end:
                    return True
        return False


@dataclass
class SafetyCheckRecord:
    """보호대상자가 안부 확인을 누른 기록을 나타낸다."""

    record_id: str  # 안부 확인 기록 ID
    protected_user_id: str  # 안부 확인을 수행한 보호대상자 사용자 ID
    status: SafetyStatus  # 안부 확인 결과 상태
    checked_at: datetime  # 보호대상자가 안부 확인을 수행한 시각

    def is_safe(self) -> bool:
        """안부 확인 기록이 안전 상태인지 확인한다."""
        return self.status == SafetyStatus.SAFE
