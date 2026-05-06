"""재난별 대처법 안내 조회 서비스를 정의한다."""

from app.domain.action_guide import ActionGuideRule
from app.domain.disaster import DisasterCatalog
from app.domain.enums import ProtectedCategory
from app.service.disaster_catalog_service import DisasterCatalogService


class ActionGuideService:
    """상시 조회 가능한 재난별 대처법 안내 API를 제공한다."""

    def __init__(self, catalog_service: DisasterCatalogService) -> None:
        self.catalog_service = catalog_service

    def list_guides(
        self,
        catalog: DisasterCatalog,
        disaster_type: str,
        categories: list[ProtectedCategory],
    ) -> list[ActionGuideRule]:
        """재난 종류와 보호대상자 분류에 맞는 대처법 안내 페이지를 조회한다."""
        raise NotImplementedError
