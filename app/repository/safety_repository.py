"""안부 설정과 안부 기록 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.domain.safety import SafetyCheckRecord, SafetySchedule


class SafetyRepository(ABC):
    """정기 안부 설정과 안부 확인 기록을 저장하고 조회한다."""

    @abstractmethod
    def save_schedule(self, schedule: SafetySchedule) -> None:
        """보호자가 설정한 정기 안부 확인 규칙을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def get_schedule(self, protected_user_id: str) -> SafetySchedule | None:
        """보호대상자의 정기 안부 확인 규칙을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def save_check_record(self, record: SafetyCheckRecord) -> None:
        """보호대상자의 안부 확인 기록을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def get_latest_check_record(self, protected_user_id: str) -> SafetyCheckRecord | None:
        """보호대상자의 최근 안부 확인 기록을 조회한다."""
        raise NotImplementedError
