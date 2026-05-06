"""체크리스트 수행 기록 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.domain.checklist import ChecklistRecord


class ChecklistRepository(ABC):
    """재난 체크리스트 수행 기록을 저장하고 조회한다."""

    @abstractmethod
    def save_record(self, record: ChecklistRecord) -> None:
        """체크리스트 수행 기록을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def list_recent_records(self, protected_user_id: str, limit: int = 3) -> list[ChecklistRecord]:
        """보호자의 조회를 위해 최근 재난 체크리스트 기록을 조회한다."""
        raise NotImplementedError
