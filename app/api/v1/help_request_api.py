"""도움 요청 및 도움 요청 위치 공유 API를 담당한다."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_help_request_service
from app.dto.help_request_dto import HelpRequestCreate, HelpRequestResponse
from app.service.help_request_service import HelpRequestService

router = APIRouter(prefix="/help-requests", tags=["help-requests"])


@router.post("/{protected_user_id}", response_model=HelpRequestResponse)
def request_help(
    protected_user_id: str,
    payload: HelpRequestCreate,
    service: HelpRequestService = Depends(get_help_request_service),
) -> HelpRequestResponse:
    """보호대상자의 도움 요청을 생성하고 현재 위치를 함께 공유한다."""
    raise NotImplementedError
