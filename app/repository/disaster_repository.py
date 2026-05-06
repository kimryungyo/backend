"""재난 이벤트와 재난 카탈로그 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.disaster import DisasterCatalog, DisasterEvent


class DisasterCatalogRepository(ABC):
    """JSON 기반 재난 카탈로그를 로드하고 저장한다."""

    @abstractmethod
    def load_catalog(self, source_path: Path) -> DisasterCatalog:
        """JSON 파일에서 재난 정의, 체크리스트, 대처법 안내를 읽어온다."""
        raise NotImplementedError

    @abstractmethod
    def save_catalog(self, catalog: DisasterCatalog, target_path: Path) -> None:
        """재난 카탈로그를 JSON 파일로 저장한다."""
        raise NotImplementedError


class DisasterEventRepository(ABC):
    """외부 API에서 수신한 재난 상황을 저장하고 조회한다."""

    @abstractmethod
    def save_event(self, event: DisasterEvent) -> None:
        """재난 상황 정보를 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def list_active_events(self, region_code: str) -> list[DisasterEvent]:
        """특정 지역에 적용 중인 재난 상황 목록을 조회한다."""
        raise NotImplementedError
