"""안부 확인, 정기 안부 설정, 미응답 조회 API를 담당한다."""

from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.dependencies import get_safety_check_service
from app.dto.safety_dto import SafetyCheckCreate, SafetyCheckResponse, SafetyScheduleResponse, SafetyScheduleUpdateRequest
from app.service.safety_service import SafetyCheckService

router = APIRouter(prefix="/safety", tags=["safety"])


@router.put("/schedule", response_model=SafetyScheduleResponse)
def configure_schedule(
    payload: SafetyScheduleUpdateRequest,
    service: SafetyCheckService = Depends(get_safety_check_service),
) -> SafetyScheduleResponse:
    """보호자가 정기 안부 시간대와 여유시간을 설정한다."""
    raise NotImplementedError


@router.post("/checks/{protected_user_id}", response_model=SafetyCheckResponse)
def record_safety_check(
    protected_user_id: str,
    payload: SafetyCheckCreate,
    service: SafetyCheckService = Depends(get_safety_check_service),
) -> SafetyCheckResponse:
    """보호대상자의 안부 확인 입력을 기록한다."""
    raise NotImplementedError


@router.get("/protected/{protected_user_id}/nonresponse", response_model=bool)
def detect_nonresponse(
    protected_user_id: str,
    now: datetime,
    service: SafetyCheckService = Depends(get_safety_check_service),
) -> bool:
    """정기 안부 설정 기준으로 미응답 여부를 조회한다."""
    raise NotImplementedError
