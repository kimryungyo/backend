"""FastAPI Depends에서 AppContext와 Service를 꺼내는 의존성 함수를 정의한다."""

from typing import cast

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.config.context import AppContext
from app.domain.user import User
from app.repository.user_repository import UserRepository
from app.security.jwt import (
    JwtSecretNotConfiguredError,
    JwtTokenExpiredError,
    JwtTokenInvalidError,
    JwtTokenManager,
)
from app.service.action_guide_service import ActionGuideService
from app.service.auth_service import AuthService
from app.service.checklist_service import ChecklistService
from app.service.connection_service import ConnectionService
from app.service.disaster_catalog_service import DisasterCatalogService
from app.service.help_request_service import HelpRequestService
from app.service.location_service import LocationShareService
from app.service.profile_service import ProfileService
from app.service.safety_service import SafetyCheckService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/kakao-login")


def get_context(request: Request) -> AppContext:
    """FastAPI 앱 상태에서 AppContext를 반환한다."""
    return request.app.state.context


def _require(value: object | None, name: str) -> object:
    """아직 연결되지 않은 의존성을 사용할 때 명확한 오류를 발생시킨다."""
    if value is None:
        raise RuntimeError(f"{name} is not configured")
    return value


def _credentials_exception(detail: str = "Could not validate credentials") -> HTTPException:
    """Bearer token 인증 실패 응답을 생성한다."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> User:
    """JWT access token을 검증하고 현재 인증된 사용자를 반환한다."""
    context = get_context(request)
    token_manager = JwtTokenManager(context.settings)
    try:
        claims = token_manager.verify_access_token(token)
    except JwtSecretNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT authentication is not configured",
        ) from exc
    except JwtTokenExpiredError as exc:
        raise _credentials_exception("Token has expired") from exc
    except JwtTokenInvalidError as exc:
        raise _credentials_exception() from exc

    user_repository = cast(UserRepository, _require(context.user_repository, "user_repository"))
    user = user_repository.find_by_id(claims.user_id)
    if user is None:
        raise _credentials_exception()
    return user


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
