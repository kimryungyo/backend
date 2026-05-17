"""재난 체크리스트 조회 및 수행 기록 API를 담당한다."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_checklist_service, get_context, get_current_user
from app.config.context import AppContext
from app.domain.checklist import ChecklistRecord
from app.domain.user import User
from app.dto.checklist_dto import (
    ChecklistCompleteRequest,
    ChecklistRecordListResponse,
    ChecklistRecordResponse,
    ChecklistRuleResponse,
)
from app.service.checklist_service import ChecklistService

router = APIRouter(prefix="/checklists", tags=["checklists"])


def _to_record_response(record: ChecklistRecord) -> ChecklistRecordResponse:
    """체크리스트 기록 도메인 모델을 응답 DTO로 변환한다."""
    return ChecklistRecordResponse(**asdict(record))


@router.get("/rules", response_model=list[ChecklistRuleResponse])
def list_checklist_rules(
    disaster_type: str,
    protected_user_id: str,
    service: ChecklistService = Depends(get_checklist_service),
    context: AppContext = Depends(get_context),
) -> list[ChecklistRuleResponse]:
    """현재 재난 상황과 보호대상자 프로필에 맞는 체크리스트를 조회한다."""
    try:
        catalog = service.catalog_service.load_catalog(context.settings.disaster_catalog_path)
        rules = service.list_checklist_rules(catalog, disaster_type, protected_user_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protected profile not found",
        ) from exc
    return [ChecklistRuleResponse(**asdict(rule)) for rule in rules]


@router.post("/records/{protected_user_id}", response_model=ChecklistRecordResponse)
def record_checklist_completion(
    protected_user_id: str,
    payload: ChecklistCompleteRequest,
    service: ChecklistService = Depends(get_checklist_service),
) -> ChecklistRecordResponse:
    """보호대상자의 체크리스트 수행 완료를 기록한다."""
    raise NotImplementedError


@router.get("/records/{protected_user_id}", response_model=ChecklistRecordListResponse)
def list_recent_checklist_records(
    protected_user_id: str,
    service: ChecklistService = Depends(get_checklist_service),
    current_user: User = Depends(get_current_user),
) -> ChecklistRecordListResponse:
    """보호자가 연결된 보호대상자의 최근 재난 체크리스트 수행 기록을 조회한다."""
    if not current_user.is_guardian():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only guardians can view checklist records",
        )

    try:
        records = service.list_recent_records_for_guardian(current_user.user_id, protected_user_id)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access checklist records for this protected user",
        ) from exc

    record_responses = [_to_record_response(record) for record in records]
    return ChecklistRecordListResponse(
        protected_user_id=protected_user_id,
        has_records=bool(record_responses),
        records=record_responses,
    )
