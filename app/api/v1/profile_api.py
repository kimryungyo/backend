"""보호대상자 분류와 자동 위치 공유 설정 API를 담당한다."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_profile_service
from app.dto.profile_dto import (
    AutoLocationShareUpdateRequest,
    ProtectedProfileResponse,
    ProtectedProfileUpdateRequest,
)
from app.service.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.put("/protected/{protected_user_id}", response_model=ProtectedProfileResponse)
def update_protected_profile(
    protected_user_id: str,
    payload: ProtectedProfileUpdateRequest,
    service: ProfileService = Depends(get_profile_service),
) -> ProtectedProfileResponse:
    """보호대상자의 분류와 지역 정보를 수정한다."""
    raise NotImplementedError


@router.patch("/protected/{protected_user_id}/auto-location-share", response_model=ProtectedProfileResponse)
def update_auto_location_share(
    protected_user_id: str,
    payload: AutoLocationShareUpdateRequest,
    service: ProfileService = Depends(get_profile_service),
) -> ProtectedProfileResponse:
    """위치 요청 미응답 시 자동 공유 설정을 변경한다."""
    raise NotImplementedError
