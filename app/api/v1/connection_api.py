"""연결 요청, 수락, 거절, 해제 API를 담당한다."""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_connection_service
from app.dto.connection_dto import ConnectionRequestCreate, ConnectionRequestResponse, ConnectionResponse
from app.service.connection_service import ConnectionService

router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("/requests", response_model=ConnectionRequestResponse)
def request_connection(
    requester_user_id: str,
    payload: ConnectionRequestCreate,
    service: ConnectionService = Depends(get_connection_service),
) -> ConnectionRequestResponse:
    """상대방 연결 아이디로 연결 요청을 보낸다."""
    raise NotImplementedError


@router.post("/requests/{request_id}/accept", response_model=ConnectionResponse)
def accept_connection_request(
    request_id: str,
    responder_user_id: str,
    service: ConnectionService = Depends(get_connection_service),
) -> ConnectionResponse:
    """받은 연결 요청을 수락해 보호자-보호대상자 연결을 생성한다."""
    raise NotImplementedError


@router.post("/requests/{request_id}/reject", response_model=ConnectionRequestResponse)
def reject_connection_request(
    request_id: str,
    responder_user_id: str,
    service: ConnectionService = Depends(get_connection_service),
) -> ConnectionRequestResponse:
    """받은 연결 요청을 거절한다."""
    raise NotImplementedError


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def disconnect(
    connection_id: str,
    requested_by_user_id: str,
    service: ConnectionService = Depends(get_connection_service),
) -> None:
    """연결을 해제하고 해당 연결 관련 기록을 삭제한다."""
    raise NotImplementedError
