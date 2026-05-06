"""상시 조회 가능한 재난별 대처법 안내 API를 담당한다."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_action_guide_service
from app.domain.enums import ProtectedCategory
from app.dto.action_guide_dto import ActionGuideRuleResponse
from app.service.action_guide_service import ActionGuideService

router = APIRouter(prefix="/action-guides", tags=["action-guides"])


@router.get("", response_model=list[ActionGuideRuleResponse])
def list_action_guides(
    disaster_type: str,
    categories: list[ProtectedCategory],
    service: ActionGuideService = Depends(get_action_guide_service),
) -> list[ActionGuideRuleResponse]:
    """재난 종류와 보호대상자 분류에 맞는 대처법 안내를 조회한다."""
    raise NotImplementedError
