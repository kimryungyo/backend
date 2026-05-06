"""v1 API 하위 라우터들을 하나로 묶는다."""

from fastapi import APIRouter

from app.api.v1 import (
    action_guide_api,
    auth_api,
    checklist_api,
    connection_api,
    disaster_api,
    help_request_api,
    location_api,
    profile_api,
    safety_api,
)

router = APIRouter()
router.include_router(auth_api.router)
router.include_router(profile_api.router)
router.include_router(connection_api.router)
router.include_router(safety_api.router)
router.include_router(disaster_api.router)
router.include_router(checklist_api.router)
router.include_router(action_guide_api.router)
router.include_router(location_api.router)
router.include_router(help_request_api.router)
