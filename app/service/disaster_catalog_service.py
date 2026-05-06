"""JSON 기반 재난 확장 카탈로그 서비스를 정의한다."""

from pathlib import Path

from app.domain.disaster import DisasterCatalog, DisasterDefinition
from app.repository.disaster_repository import DisasterCatalogRepository


class DisasterCatalogService:
    """재난 카탈로그를 검증하고 재난별 정책을 조회한다."""

    def __init__(self, catalog_repository: DisasterCatalogRepository) -> None:
        self.catalog_repository = catalog_repository

    def load_catalog(self, source_path: Path) -> DisasterCatalog:
        """JSON 재난 카탈로그를 로드한다."""
        raise NotImplementedError

    def validate_catalog(self, catalog: DisasterCatalog) -> None:
        """재난, 체크리스트, 대처법 안내 확장 데이터의 기본 형식을 검증한다."""
        raise NotImplementedError

    def find_definition(self, catalog: DisasterCatalog, disaster_type: str) -> DisasterDefinition | None:
        """재난 종류 코드에 해당하는 재난 정의를 조회한다."""
        raise NotImplementedError
