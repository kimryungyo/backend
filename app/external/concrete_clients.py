"""운영 코드에서 주입할 concrete 외부 연동 client 구현체를 정의한다."""

from datetime import datetime, timezone
from typing import Any

import httpx

from app.config.settings import Settings
from app.domain.disaster import DisasterEvent
from app.domain.location import GeoLocation
from app.domain.notification import NotificationMessage
from app.external.disaster_info_client import DisasterInfoClient
from app.external.kakao_oauth_client import KakaoOAuthClient
from app.external.location_provider_client import LocationProviderClient
from app.external.push_notification_client import PushNotificationClient


class KakaoOAuthHttpClient(KakaoOAuthClient):
    """카카오 사용자 정보 API로 access token을 검증한다."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.kakao_oauth_base_url.rstrip("/")

    def verify_token(self, access_token: str) -> dict[str, Any]:
        """카카오 access token을 검증하고 사용자 식별 정보를 반환한다."""
        response = httpx.get(
            f"{self._base_url}/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json()


class NoopPushNotificationClient(PushNotificationClient):
    """외부 푸시 사업자 연동 전까지 사용하는 no-op push client."""

    def send(self, message: NotificationMessage) -> None:
        """알림 메시지를 전송 완료로 표시한다."""
        message.mark_sent(datetime.now(timezone.utc))


class UnavailableLocationProviderClient(LocationProviderClient):
    """위치 제공자 연동 전까지 명확한 오류를 반환하는 client."""

    def get_current_location(self, protected_user_id: str) -> GeoLocation:
        """보호대상자의 현재 위치 정보를 조회한다."""
        raise RuntimeError(f"location provider is not configured: {protected_user_id}")


class EmptyDisasterInfoClient(DisasterInfoClient):
    """외부 재난 정보 API 연동 전까지 빈 재난 목록을 반환하는 client."""

    def fetch_active_events(self, region_code: str) -> list[DisasterEvent]:
        """특정 지역의 현재 재난 상황 목록을 조회한다."""
        return []
