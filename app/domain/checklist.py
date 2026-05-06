"""재난 체크리스트 규칙과 기록 도메인 모델을 정의한다."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.domain.enums import ProtectedCategory


@dataclass
class ChecklistRule:
    """재난 종류와 보호대상자 분류에 따라 제공되는 체크리스트 규칙을 나타낸다."""

    rule_id: str  # 체크리스트 규칙 ID
    disaster_type: str  # 이 규칙이 적용되는 재난 종류 코드
    category: ProtectedCategory  # 이 규칙이 적용되는 보호대상자 분류
    title: str  # 보호대상자에게 표시할 체크리스트 항목 이름
    interval_minutes: int  # 체크리스트 반복 제공 주기
    enabled: bool  # 규칙 사용 여부

    def applies_to(self, disaster_type: str, categories: list[ProtectedCategory]) -> bool:
        """재난 종류와 보호대상자 분류에 이 규칙이 적용되는지 확인한다."""
        return self.enabled and self.disaster_type == disaster_type and self.category in categories

    def next_due_after(self, completed_at: datetime) -> datetime:
        """체크리스트 완료 시각 이후 다음 수행 예정 시각을 계산한다."""
        return completed_at + timedelta(minutes=self.interval_minutes)


@dataclass
class ChecklistRecord:
    """보호대상자가 재난 체크리스트를 수행한 기록을 나타낸다."""

    record_id: str  # 체크리스트 수행 기록 ID
    protected_user_id: str  # 체크리스트를 수행한 보호대상자 사용자 ID
    disaster_event_id: str  # 수행 기록이 연결된 재난 상황 ID
    checklist_rule_id: str  # 수행한 체크리스트 규칙 ID
    completed_at: datetime  # 체크리스트 수행 완료 시각

    def is_for_rule(self, checklist_rule_id: str) -> bool:
        """이 기록이 특정 체크리스트 규칙에 대한 수행 기록인지 확인한다."""
        return self.checklist_rule_id == checklist_rule_id

    def is_for_event(self, disaster_event_id: str) -> bool:
        """이 기록이 특정 재난 상황에 대한 수행 기록인지 확인한다."""
        return self.disaster_event_id == disaster_event_id
