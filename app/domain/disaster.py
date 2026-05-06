"""재난 상황과 재난 카탈로그 도메인 모델을 정의한다."""

from dataclasses import dataclass, field
from datetime import datetime

from app.domain.action_guide import ActionGuideRule
from app.domain.checklist import ChecklistRule
from app.domain.enums import ProtectedCategory


@dataclass
class DisasterEvent:
    """외부 재난 정보 API에서 수신한 실제 재난 상황을 나타낸다."""

    event_id: str  # 재난 상황 ID
    disaster_type: str  # 폭염, 화재, 지진 등 재난 종류 코드
    region_code: str  # 재난이 적용되는 지역 코드
    alert_level: str  # 외부 API 또는 내부 정책의 경보 수준
    started_at: datetime  # 재난 상황 시작 시각
    ended_at: datetime | None = None  # 재난 상황 종료 시각

    def is_active(self, now: datetime) -> bool:
        """현재 시각 기준으로 재난 상황이 진행 중인지 확인한다."""
        return self.started_at <= now and (self.ended_at is None or now <= self.ended_at)

    def affects_region(self, region_code: str) -> bool:
        """재난 상황이 지정한 지역에 적용되는지 확인한다."""
        return self.region_code == region_code

    def is_type(self, disaster_type: str) -> bool:
        """재난 상황이 지정한 재난 종류인지 확인한다."""
        return self.disaster_type == disaster_type


@dataclass
class DisasterDefinition:
    """JSON 카탈로그에 저장되는 확장 가능한 재난 정의를 나타낸다."""

    disaster_type: str  # 재난 종류 코드
    display_name: str  # 화면에 표시할 재난 이름
    checklist_rules: list[ChecklistRule] = field(default_factory=list)  # 재난 상황에서 제공할 체크리스트 규칙
    guide_rules: list[ActionGuideRule] = field(default_factory=list)  # 상시 제공할 재난별 대처법 안내

    def checklist_rules_for(self, categories: list[ProtectedCategory]) -> list[ChecklistRule]:
        """보호대상자 분류에 맞는 활성 체크리스트 규칙을 반환한다."""
        return [rule for rule in self.checklist_rules if rule.applies_to(self.disaster_type, categories)]

    def guide_rules_for(self, categories: list[ProtectedCategory]) -> list[ActionGuideRule]:
        """보호대상자 분류에 맞는 활성 대처법 안내를 반환한다."""
        return [rule for rule in self.guide_rules if rule.applies_to(self.disaster_type, categories)]


@dataclass
class DisasterCatalog:
    """재난 종류, 체크리스트, 대처법 안내를 묶은 JSON 기반 카탈로그를 나타낸다."""

    version: str  # 재난 카탈로그 버전
    disasters: list[DisasterDefinition]  # 서비스가 지원하는 재난 정의 목록
    updated_at: datetime  # 카탈로그가 마지막으로 수정된 시각

    def find_definition(self, disaster_type: str) -> DisasterDefinition | None:
        """재난 종류 코드에 해당하는 재난 정의를 찾는다."""
        return next((disaster for disaster in self.disasters if disaster.disaster_type == disaster_type), None)

    def supported_disaster_types(self) -> list[str]:
        """카탈로그가 지원하는 재난 종류 코드 목록을 반환한다."""
        return [disaster.disaster_type for disaster in self.disasters]
