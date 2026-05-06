"""FastAPI Depends에서 AppContext와 Service를 꺼내는 의존성 함수를 정의한다."""

from fastapi import Request

from app.config.context import AppContext
from app.service.action_guide_service import ActionGuideService
from app.service.auth_service import AuthService
from app.service.checklist_service import ChecklistService
from app.service.connection_service import ConnectionService
from app.service.disaster_catalog_service import DisasterCatalogService
from app.service.help_request_service import HelpRequestService
from app.service.location_service import LocationShareService
from app.service.profile_service import ProfileService
from app.service.safety_service import SafetyCheckService


def get_context(request: Request) -> AppContext:
    """FastAPI 앱 상태에서 AppContext를 반환한다."""
    return request.app.state.context


def _require(value: object | None, name: str) -> object:
    """아직 연결되지 않은 의존성을 사용할 때 명확한 오류를 발생시킨다."""
    if value is None:
        raise RuntimeError(f"{name} is not configured")
    return value


def get_auth_service(request: Request) -> AuthService:
    """AuthService 의존성을 반환한다."""
    return _require(get_context(request).auth_service, "auth_service")  # type: ignore[return-value]


def get_profile_service(request: Request) -> ProfileService:
    """ProfileService 의존성을 반환한다."""
    return _require(get_context(request).profile_service, "profile_service")  # type: ignore[return-value]


def get_connection_service(request: Request) -> ConnectionService:
    """ConnectionService 의존성을 반환한다."""
    return _require(get_context(request).connection_service, "connection_service")  # type: ignore[return-value]


def get_safety_check_service(request: Request) -> SafetyCheckService:
    """SafetyCheckService 의존성을 반환한다."""
    return _require(get_context(request).safety_check_service, "safety_check_service")  # type: ignore[return-value]


def get_disaster_catalog_service(request: Request) -> DisasterCatalogService:
    """DisasterCatalogService 의존성을 반환한다."""
    return _require(get_context(request).disaster_catalog_service, "disaster_catalog_service")  # type: ignore[return-value]


def get_checklist_service(request: Request) -> ChecklistService:
    """ChecklistService 의존성을 반환한다."""
    return _require(get_context(request).checklist_service, "checklist_service")  # type: ignore[return-value]


def get_action_guide_service(request: Request) -> ActionGuideService:
    """ActionGuideService 의존성을 반환한다."""
    return _require(get_context(request).action_guide_service, "action_guide_service")  # type: ignore[return-value]


def get_location_share_service(request: Request) -> LocationShareService:
    """LocationShareService 의존성을 반환한다."""
    return _require(get_context(request).location_share_service, "location_share_service")  # type: ignore[return-value]


def get_help_request_service(request: Request) -> HelpRequestService:
    """HelpRequestService 의존성을 반환한다."""
    return _require(get_context(request).help_request_service, "help_request_service")  # type: ignore[return-value]
