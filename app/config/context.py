"""Repository, Service, 외부 Client를 DI로 주입하기 위한 AppContext를 정의한다."""

from dataclasses import dataclass

from app.config.settings import Settings
from app.external.disaster_info_client import DisasterInfoClient
from app.external.kakao_oauth_client import KakaoOAuthClient
from app.external.location_provider_client import LocationProviderClient
from app.external.push_notification_client import PushNotificationClient
from app.repository.checklist_repository import ChecklistRepository
from app.repository.connection_repository import ConnectionRepository
from app.repository.disaster_repository import DisasterCatalogRepository, DisasterEventRepository
from app.repository.location_repository import LocationRepository
from app.repository.notification_repository import NotificationRepository
from app.repository.profile_repository import ProfileRepository
from app.repository.safety_repository import SafetyRepository
from app.repository.user_repository import UserRepository
from app.service.action_guide_service import ActionGuideService
from app.service.auth_service import AuthService
from app.service.checklist_service import ChecklistService
from app.service.connection_service import ConnectionService
from app.service.disaster_catalog_service import DisasterCatalogService
from app.service.help_request_service import HelpRequestService
from app.service.location_service import LocationShareService
from app.service.notification_service import NotificationService
from app.service.profile_service import ProfileService
from app.service.safety_service import SafetyCheckService


@dataclass
class AppContext:
    """FastAPI dependency로 주입할 애플리케이션 의존성 묶음이다."""

    settings: Settings  # 환경변수와 서버 설정 값
    kakao_oauth_client: KakaoOAuthClient | None = None  # 카카오 OAuth 연동 클라이언트
    push_notification_client: PushNotificationClient | None = None  # 푸시 알림 연동 클라이언트
    location_provider_client: LocationProviderClient | None = None  # 위치 조회 연동 클라이언트
    disaster_info_client: DisasterInfoClient | None = None  # 외부 재난 정보 API 클라이언트
    user_repository: UserRepository | None = None  # 사용자 저장소
    profile_repository: ProfileRepository | None = None  # 프로필 저장소
    connection_repository: ConnectionRepository | None = None  # 연결 저장소
    safety_repository: SafetyRepository | None = None  # 안부 확인 저장소
    disaster_catalog_repository: DisasterCatalogRepository | None = None  # 재난 카탈로그 저장소
    disaster_event_repository: DisasterEventRepository | None = None  # 재난 이벤트 저장소
    checklist_repository: ChecklistRepository | None = None  # 체크리스트 저장소
    location_repository: LocationRepository | None = None  # 위치 요청 저장소
    notification_repository: NotificationRepository | None = None  # 알림 저장소
    auth_service: AuthService | None = None  # 인증 서비스
    profile_service: ProfileService | None = None  # 프로필 서비스
    connection_service: ConnectionService | None = None  # 연결 서비스
    safety_check_service: SafetyCheckService | None = None  # 안부 확인 서비스
    disaster_catalog_service: DisasterCatalogService | None = None  # 재난 카탈로그 서비스
    checklist_service: ChecklistService | None = None  # 체크리스트 서비스
    action_guide_service: ActionGuideService | None = None  # 재난별 대처법 안내 서비스
    location_share_service: LocationShareService | None = None  # 위치 공유 서비스
    help_request_service: HelpRequestService | None = None  # 도움 요청 서비스
    notification_service: NotificationService | None = None  # 알림 서비스


def create_app_context(settings: Settings | None = None) -> AppContext:
    """애플리케이션 시작 시 DI context를 생성한다."""
    return AppContext(settings=settings or Settings())
