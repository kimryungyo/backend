"""위치 요청, 승인, 거절, 자동 공유 API를 담당한다."""

from dataclasses import asdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_location_share_service
from app.domain.user import User
from app.dto.location_dto import LocationRequestCreate, LocationRequestResponse, LocationShareResponse
from app.service.location_service import LocationShareService

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/requests", response_model=LocationRequestResponse)
def request_location(
    payload: LocationRequestCreate,
    service: LocationShareService = Depends(get_location_share_service),
    current_user: User = Depends(get_current_user),
) -> LocationRequestResponse:
    """보호자가 보호대상자에게 위치 공유 요청을 보낸다."""
    # 1. 권한 확인: 보호자만 위치 요청을 보낼 수 있다.
    if not current_user.is_guardian():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only guardians can request location sharing",
        )

    try:
        # 2. 서비스 계층을 통해 위치 요청을 생성한다.
        request = service.request_location(
            guardian_user_id=current_user.user_id,
            protected_user_id=payload.protected_user_id,
            requested_at=datetime.now(timezone.utc),
        )
    except ValueError as exc:
        # 연결이 없거나 사용자를 찾을 수 없는 경우
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # 3. 도메인 모델을 응답 DTO로 변환하여 반환한다.
    return LocationRequestResponse(**asdict(request))


@router.post("/requests/{request_id}/approve", response_model=LocationShareResponse)
def approve_location_request(
    request_id: str,
    service: LocationShareService = Depends(get_location_share_service),
    current_user: User = Depends(get_current_user),
) -> LocationShareResponse:
    """보호대상자가 위치 요청을 승인하고 현재 위치를 공유한다."""
    # 1. 권한 확인: 보호대상자만 자신의 위치 요청을 승인할 수 있다.
    if not current_user.is_protected():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only protected users can approve location requests",
        )

    try:
        # 2. 서비스 계층을 통해 위치 요청 승인 및 위치 공유 기록 생성
        share_record = service.approve_location_request(
            request_id=request_id,
            protected_user_id=current_user.user_id,
        )
    except (ValueError, KeyError) as exc:
        # 요청이 없거나, 대상자가 다르거나, 대기 상태가 아닌 경우
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # 3. 도메인 모델을 응답 DTO로 변환하여 반환한다.
    return LocationShareResponse(**asdict(share_record))


@router.post("/requests/{request_id}/reject", response_model=LocationRequestResponse)
def reject_location_request(
    request_id: str,
    service: LocationShareService = Depends(get_location_share_service),
    current_user: User = Depends(get_current_user),
) -> LocationRequestResponse:
    """보호대상자가 위치 요청을 거절한다."""
    # 1. 권한 확인: 보호대상자만 자신의 위치 요청을 거절할 수 있다.
    if not current_user.is_protected():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only protected users can reject location requests",
        )

    try:
        # 2. 서비스 계층을 통해 위치 요청 거절 처리
        request = service.reject_location_request(
            request_id=request_id,
            protected_user_id=current_user.user_id,
        )
    except (ValueError, KeyError) as exc:
        # 요청이 없거나, 대상자가 다르거나, 대기 상태가 아닌 경우
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # 3. 도메인 모델을 응답 DTO로 변환하여 반환한다.
    return LocationRequestResponse(**asdict(request))


@router.post("/requests/{request_id}/auto-share", response_model=LocationShareResponse | None)
def auto_share_after_timeout(
    request_id: str,
    service: LocationShareService = Depends(get_location_share_service),
) -> LocationShareResponse | None:
    """30분 미응답과 자동 공유 설정을 확인해 위치를 공유한다."""
    # 시스템 워커나 스케줄러에 의해 호출되는 엔드포인트이므로,
    # 현재 시각(now)은 서버에서 직접 결정한다.
    now = datetime.now(timezone.utc)
    
    try:
        # 서비스 계층에서 미응답 조건 및 자동 공유 설정 확인 후 처리
        share_record = service.auto_share_after_timeout(request_id, now)
        
        if share_record is None:
            # 조건이 맞지 않아 공유되지 않은 경우 (예: 아직 30분이 안 지남, 자동 공유 비활성 등)
            return None
            
        return LocationShareResponse(**asdict(share_record))
        
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location request not found: {request_id}",
        ) from exc
