"""재난별 체크리스트 조회와 수행 기록 서비스를 정의한다."""

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
        raise NotImplementedError

    def record_completion(
        self,
        protected_user_id: str,
        disaster_event_id: str,
        checklist_rule_id: str,
        completed_at: datetime,
    ) -> ChecklistRecord:
        """보호대상자의 체크리스트 수행 완료를 기록한다."""
        raise NotImplementedError
