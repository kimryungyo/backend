"""상시 조회 가능한 재난별 대처법 안내 API를 담당한다."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_action_guide_service, get_context
from app.config.context import AppContext
from app.dto.action_guide_dto import ActionGuideRuleResponse
from app.service.action_guide_service import ActionGuideService

router = APIRouter(prefix="/action-guides", tags=["action-guides"])


@router.get("", response_model=list[ActionGuideRuleResponse])
def list_action_guides(
    disaster_type: str,
    protected_user_id: str,
    service: ActionGuideService = Depends(get_action_guide_service),
    context: AppContext = Depends(get_context),
) -> list[ActionGuideRuleResponse]:
    """현재 재난 상황과 보호대상자 프로필에 맞는 대처법 안내를 조회한다."""
    try:
        catalog = service.catalog_service.load_catalog(context.settings.disaster_catalog_path)
        guides = service.list_guides(catalog, disaster_type, protected_user_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protected profile not found",
        ) from exc
    return [ActionGuideRuleResponse(**asdict(guide)) for guide in guides]
