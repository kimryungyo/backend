"""재난별 대처법 안내 조회 서비스를 정의한다."""

from app.domain.action_guide import ActionGuideRule
from app.domain.disaster import DisasterCatalog
from app.repository.disaster_repository import DisasterEventRepository
from app.repository.profile_repository import ProfileRepository
from app.service.disaster_catalog_service import DisasterCatalogService


class ActionGuideService:
    """상시 조회 가능한 재난별 대처법 안내 API를 제공한다."""

    def __init__(
        self,
        catalog_service: DisasterCatalogService,
        profile_repository: ProfileRepository,
        disaster_event_repository: DisasterEventRepository,
    ) -> None:
        self.catalog_service = catalog_service
        self.profile_repository = profile_repository
        self.disaster_event_repository = disaster_event_repository

    def list_guides(
        self,
        catalog: DisasterCatalog,
        disaster_type: str,
        protected_user_id: str,
    ) -> list[ActionGuideRule]:
        """현재 재난 상황과 보호대상자 프로필에 맞는 대처법 안내 페이지를 조회한다."""
        profile = self.profile_repository.get_protected_profile(protected_user_id)
        active_events = self.disaster_event_repository.list_active_events(profile.region_code)
        if not any(event.is_type(disaster_type) for event in active_events):
            return []

        definition = catalog.find_definition(disaster_type)
        if not definition:
            return []
        return definition.guide_rules_for(profile.categories)
