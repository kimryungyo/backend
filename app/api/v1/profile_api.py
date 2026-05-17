"""보호대상자 분류와 자동 위치 공유 설정 API를 담당한다."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_profile_service
from app.domain.profile import ProtectedProfile
from app.domain.user import User
from app.dto.profile_dto import (
    AutoLocationShareUpdateRequest,
    ProtectedProfileResponse,
    ProtectedProfileUpdateRequest,
)
from app.service.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _require_self_protected_user(current_user: User, protected_user_id: str) -> None:
    """보호대상자 본인만 자신의 프로필을 수정할 수 있도록 검증한다."""
    if not current_user.is_protected() or current_user.user_id != protected_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the protected user can update their own profile",
        )


def _to_response(profile: ProtectedProfile) -> ProtectedProfileResponse:
    """프로필 도메인 모델을 응답 DTO로 변환한다."""
    return ProtectedProfileResponse(**asdict(profile))


@router.put("/protected/{protected_user_id}", response_model=ProtectedProfileResponse)
def update_protected_profile(
    protected_user_id: str,
    payload: ProtectedProfileUpdateRequest,
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user),
) -> ProtectedProfileResponse:
    """보호대상자의 분류와 지역 정보를 수정한다."""
    _require_self_protected_user(current_user, protected_user_id)
    profile = service.update_protected_categories(
        protected_user_id=protected_user_id,
        categories=payload.categories,
        region_code=payload.region_code,
    )
    return _to_response(profile)


@router.patch("/protected/{protected_user_id}/auto-location-share", response_model=ProtectedProfileResponse)
def update_auto_location_share(
    protected_user_id: str,
    payload: AutoLocationShareUpdateRequest,
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user),
) -> ProtectedProfileResponse:
    """위치 요청 미응답 시 자동 공유 설정을 변경한다."""
    _require_self_protected_user(current_user, protected_user_id)
    profile = service.update_auto_location_share(
        protected_user_id=protected_user_id,
        enabled=payload.enabled,
    )
    return _to_response(profile)
