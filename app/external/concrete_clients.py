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


class HttpDisasterInfoClient(DisasterInfoClient):
    """HTTP 기반 외부 재난 정보 API 클라이언트."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.disaster_info_base_url.rstrip("/")
        self._active_events_path = settings.disaster_info_active_events_path

    def fetch_active_events(self, region_code: str) -> list[DisasterEvent]:
        """특정 지역의 현재 재난 상황 목록을 조회한다."""
        if not self._base_url:
            return []

        response = httpx.get(
            f"{self._base_url}{self._active_events_path}",
            params={"region_code": region_code},
            timeout=5.0,
        )
        response.raise_for_status()
        payload = response.json()
        items = payload.get("events", payload) if isinstance(payload, dict) else payload
        return [self._to_event(item) for item in items]

    def _to_event(self, item: dict[str, Any]) -> DisasterEvent:
        """외부 API 응답 한 건을 내부 재난 이벤트로 변환한다."""
        return DisasterEvent(
            event_id=str(item["event_id"]),
            disaster_type=str(item["disaster_type"]),
            region_code=str(item["region_code"]),
            alert_level=str(item["alert_level"]),
            started_at=self._to_datetime(item["started_at"]),
            ended_at=self._to_datetime(item["ended_at"]) if item.get("ended_at") else None,
        )

    def _to_datetime(self, value: str | datetime) -> datetime:
        """ISO-8601 문자열 또는 datetime 값을 datetime으로 변환한다."""
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


class EmptyDisasterInfoClient(DisasterInfoClient):
    """외부 재난 정보 API 연동 전까지 빈 재난 목록을 반환하는 client."""

    def fetch_active_events(self, region_code: str) -> list[DisasterEvent]:
        """특정 지역의 현재 재난 상황 목록을 조회한다."""
        return []
