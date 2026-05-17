"""도움 요청 및 도움 요청 위치 공유 API를 담당한다."""

from dataclasses import asdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_help_request_service
from app.domain.user import User
from app.dto.help_request_dto import HelpRequestCreate, HelpRequestResponse
from app.service.help_request_service import HelpRequestService

router = APIRouter(prefix="/help-requests", tags=["help-requests"])


@router.post("/{protected_user_id}", response_model=HelpRequestResponse)
def request_help(
    protected_user_id: str,
    payload: HelpRequestCreate,
    service: HelpRequestService = Depends(get_help_request_service),
    current_user: User = Depends(get_current_user),
) -> HelpRequestResponse:
    """보호대상자의 도움 요청을 생성하고 현재 위치를 함께 공유한다."""
    # 1. 권한 확인: 보호대상자 본인만 도움 요청을 보낼 수 있다.
    if not current_user.is_protected() or current_user.user_id != protected_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the protected user can request help for themselves",
        )

    # 2. 요청 시각 설정 (페이로드에 없으면 현재 시각 사용)
    requested_at = payload.requested_at or datetime.now(timezone.utc)

    try:
        # 3. 서비스 계층을 통해 도움 요청 처리 (위치 공유 및 알림 포함)
        record = service.request_help(
            protected_user_id=protected_user_id,
            requested_at=requested_at,
        )
    except ValueError as exc:
        # 연결된 보호자가 없는 경우 등
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # 4. 도메인 모델을 응답 DTO로 변환하여 반환한다.
    return HelpRequestResponse(**asdict(record))
