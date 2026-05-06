"""재난 카탈로그와 현재 재난 상황 조회 API를 담당한다."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_disaster_catalog_service
from app.dto.disaster_dto import DisasterCatalogResponse, DisasterEventResponse
from app.service.disaster_catalog_service import DisasterCatalogService

router = APIRouter(prefix="/disasters", tags=["disasters"])


@router.get("/catalog", response_model=DisasterCatalogResponse)
def get_disaster_catalog(
    service: DisasterCatalogService = Depends(get_disaster_catalog_service),
) -> DisasterCatalogResponse:
    """확장 가능한 재난 카탈로그를 조회한다."""
    raise NotImplementedError


@router.get("/events/active", response_model=list[DisasterEventResponse])
def list_active_disaster_events(region_code: str) -> list[DisasterEventResponse]:
    """특정 지역에 적용 중인 현재 재난 상황 목록을 조회한다."""
    raise NotImplementedError
