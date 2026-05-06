"""재난 체크리스트 조회 및 수행 기록 API를 담당한다."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_checklist_service
from app.domain.enums import ProtectedCategory
from app.dto.checklist_dto import ChecklistCompleteRequest, ChecklistRecordResponse, ChecklistRuleResponse
from app.service.checklist_service import ChecklistService

router = APIRouter(prefix="/checklists", tags=["checklists"])


@router.get("/rules", response_model=list[ChecklistRuleResponse])
def list_checklist_rules(
    disaster_type: str,
    categories: list[ProtectedCategory],
    service: ChecklistService = Depends(get_checklist_service),
) -> list[ChecklistRuleResponse]:
    """재난 종류와 보호대상자 분류에 맞는 체크리스트를 조회한다."""
    raise NotImplementedError


@router.post("/records/{protected_user_id}", response_model=ChecklistRecordResponse)
def record_checklist_completion(
    protected_user_id: str,
    payload: ChecklistCompleteRequest,
    service: ChecklistService = Depends(get_checklist_service),
) -> ChecklistRecordResponse:
    """보호대상자의 체크리스트 수행 완료를 기록한다."""
    raise NotImplementedError
