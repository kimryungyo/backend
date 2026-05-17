"""재난별 체크리스트 조회와 수행 기록 서비스를 정의한다."""

import uuid
from datetime import datetime

from app.domain.checklist import ChecklistRecord, ChecklistRule
from app.domain.disaster import DisasterCatalog
from app.repository.checklist_repository import ChecklistRepository
from app.repository.connection_repository import ConnectionRepository
from app.repository.disaster_repository import DisasterEventRepository
from app.repository.profile_repository import ProfileRepository
from app.service.disaster_catalog_service import DisasterCatalogService


class ChecklistService:
    """재난 상황에서 보호대상자에게 필요한 체크리스트를 제공하고 기록한다."""

    def __init__(
        self,
        checklist_repository: ChecklistRepository,
        catalog_service: DisasterCatalogService,
        connection_repository: ConnectionRepository,
        profile_repository: ProfileRepository,
        disaster_event_repository: DisasterEventRepository,
    ) -> None:
        self.checklist_repository = checklist_repository
        self.catalog_service = catalog_service
        self.connection_repository = connection_repository
        self.profile_repository = profile_repository
        self.disaster_event_repository = disaster_event_repository

    def list_checklist_rules(
        self,
        catalog: DisasterCatalog,
        disaster_type: str,
        protected_user_id: str,
    ) -> list[ChecklistRule]:
        """현재 재난 상황과 보호대상자 프로필에 맞는 체크리스트 규칙을 조회한다."""
        profile = self.profile_repository.get_protected_profile(protected_user_id)
        active_events = self.disaster_event_repository.list_active_events(profile.region_code)
        if not any(event.is_type(disaster_type) for event in active_events):
            return []

        definition = catalog.find_definition(disaster_type)
        if not definition:
            return []

        return definition.checklist_rules_for(profile.categories)

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

    def list_recent_records_for_guardian(
        self,
        guardian_user_id: str,
        protected_user_id: str,
        limit: int = 3,
    ) -> list[ChecklistRecord]:
        """연결된 보호자가 보호대상자의 최근 체크리스트 수행 기록을 조회한다."""
        connection = self.connection_repository.find_active_by_protected(protected_user_id)
        if not connection or not connection.connects(guardian_user_id, protected_user_id):
            raise PermissionError("guardian is not connected to protected user")

        return self.checklist_repository.list_recent_records(protected_user_id, limit=limit)
