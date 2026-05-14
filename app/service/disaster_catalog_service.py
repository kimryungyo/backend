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
        catalog = self.catalog_repository.load_catalog(source_path)
        self.validate_catalog(catalog)
        return catalog

    def validate_catalog(self, catalog: DisasterCatalog) -> None:
        """재난, 체크리스트, 대처법 안내 확장 데이터의 기본 형식을 검증한다."""
        if not catalog.version:
            raise ValueError("카탈로그 버전 정보가 없습니다.")
        if not catalog.disasters:
            raise ValueError("카탈로그에 등록된 재난 정의가 없습니다.")

        disaster_types = set()
        for disaster in catalog.disasters:
            if not disaster.disaster_type:
                raise ValueError("재난 종류 코드(disaster_type)가 누락되었습니다.")
            if disaster.disaster_type in disaster_types:
                raise ValueError(f"중복된 재난 종류 코드입니다: {disaster.disaster_type}")
            disaster_types.add(disaster.disaster_type)

            if not disaster.display_name:
                raise ValueError(f"재난 표시 이름(display_name)이 누락되었습니다: {disaster.disaster_type}")

            # 체크리스트 규칙 검증
            rule_ids = set()
            for rule in disaster.checklist_rules:
                if not rule.rule_id:
                    raise ValueError(f"체크리스트 규칙 ID가 누락되었습니다: {disaster.disaster_type}")
                if rule.rule_id in rule_ids:
                    raise ValueError(f"중복된 체크리스트 규칙 ID입니다: {rule.rule_id}")
                rule_ids.add(rule.rule_id)

            # 대처법 안내 규칙 검증
            guide_ids = set()
            for guide in disaster.guide_rules:
                if not guide.guide_id:
                    raise ValueError(f"대처법 안내 ID가 누락되었습니다: {disaster.disaster_type}")
                if guide.guide_id in guide_ids:
                    raise ValueError(f"중복된 대처법 안내 ID입니다: {guide.guide_id}")
                guide_ids.add(guide.guide_id)
                if not guide.pages:
                    raise ValueError(f"대처법 안내 페이지가 없습니다: {guide.guide_id}")

    def find_definition(self, catalog: DisasterCatalog, disaster_type: str) -> DisasterDefinition | None:
        """재난 종류 코드에 해당하는 재난 정의를 조회한다."""
        return catalog.find_definition(disaster_type)
