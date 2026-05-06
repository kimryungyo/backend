"""위치 요청, 승인, 거절, 자동 공유 API를 담당한다."""

from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.dependencies import get_location_share_service
from app.dto.location_dto import LocationRequestCreate, LocationRequestResponse, LocationShareResponse
from app.service.location_service import LocationShareService

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/requests", response_model=LocationRequestResponse)
def request_location(
    guardian_user_id: str,
    payload: LocationRequestCreate,
    service: LocationShareService = Depends(get_location_share_service),
) -> LocationRequestResponse:
    """보호자가 보호대상자에게 위치 공유 요청을 보낸다."""
    raise NotImplementedError


@router.post("/requests/{request_id}/approve", response_model=LocationShareResponse)
def approve_location_request(
    request_id: str,
    protected_user_id: str,
    service: LocationShareService = Depends(get_location_share_service),
) -> LocationShareResponse:
    """보호대상자가 위치 요청을 승인하고 현재 위치를 공유한다."""
    raise NotImplementedError


@router.post("/requests/{request_id}/reject", response_model=LocationRequestResponse)
def reject_location_request(
    request_id: str,
    protected_user_id: str,
    service: LocationShareService = Depends(get_location_share_service),
) -> LocationRequestResponse:
    """보호대상자가 위치 요청을 거절한다."""
    raise NotImplementedError


@router.post("/requests/{request_id}/auto-share", response_model=LocationShareResponse | None)
def auto_share_after_timeout(
    request_id: str,
    now: datetime,
    service: LocationShareService = Depends(get_location_share_service),
) -> LocationShareResponse | None:
    """30분 미응답과 자동 공유 설정을 확인해 위치를 공유한다."""
    raise NotImplementedError
