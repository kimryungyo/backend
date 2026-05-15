"""재난별 체크리스트 조회와 수행 기록 서비스를 정의한다."""

import uuid
from datetime import datetime

from app.domain.checklist import ChecklistRecord, ChecklistRule
from app.domain.disaster import DisasterCatalog
from app.domain.enums import ProtectedCategory
from app.repository.checklist_repository import ChecklistRepository
from app.service.disaster_catalog_service import DisasterCatalogService


class ChecklistService:
    """재난 상황에서 보호대상자에게 필요한 체크리스트를 제공하고 기록한다."""

    def __init__(self, checklist_repository: ChecklistRepository, catalog_service: DisasterCatalogService) -> None:
        self.checklist_repository = checklist_repository
        self.catalog_service = catalog_service

    def list_checklist_rules(
        self,
        catalog: DisasterCatalog,
        disaster_type: str,
        categories: list[ProtectedCategory],
    ) -> list[ChecklistRule]:
        """재난 종류와 보호대상자 분류에 맞는 체크리스트 규칙을 조회한다."""
        # 1. 카탈로그에서 해당 재난의 정의를 찾는다.
        definition = catalog.find_definition(disaster_type)
        if not definition:
            return []

        # 2. 도메인 모델에 위임하여 보호대상자 분류에 맞는 규칙 목록을 반환한다.
        return definition.checklist_rules_for(categories)

    def record_completion(
        self,
        protected_user_id: str,
        disaster_event_id: str,
        checklist_rule_id: str,
        completed_at: datetime,
    ) -> ChecklistRecord:
        """보호대상자의 체크리스트 수행 완료를 기록한다."""
        # 1. 수행 기록 객체를 생성한다.
        record = ChecklistRecord(
            record_id=uuid.uuid4().hex,
            protected_user_id=protected_user_id,
            disaster_event_id=disaster_event_id,
            checklist_rule_id=checklist_rule_id,
            completed_at=completed_at,
        )

        # 2. 저장소에 기록을 저장한다.
        self.checklist_repository.save_record(record)

        return record
