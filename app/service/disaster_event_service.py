"""외부 재난 정보 수신, 저장, 긴급 알림 발송 서비스를 정의한다."""

from dataclasses import dataclass
from datetime import datetime, timezone

from app.domain.disaster import DisasterEvent
from app.external.disaster_info_client import DisasterInfoClient
from app.repository.connection_repository import ConnectionRepository
from app.repository.disaster_repository import DisasterEventRepository
from app.repository.profile_repository import ProfileRepository
from app.service.notification_service import NotificationService

EMERGENCY_ALERT_LEVELS = {"emergency", "critical", "severe", "warning", "긴급", "심각", "경계"}


@dataclass(frozen=True)
class DisasterIngestionResult:
    """재난 정보 수신 처리 결과."""

    saved_events: list[DisasterEvent]
    emergency_events: list[DisasterEvent]
    notified_guardian_user_ids: list[str]


class DisasterEventIngestionService:
    """외부 재난 정보를 저장하고 긴급 재난 알림 대상을 산정한다."""

    def __init__(
        self,
        disaster_info_client: DisasterInfoClient,
        disaster_event_repository: DisasterEventRepository,
        profile_repository: ProfileRepository,
        connection_repository: ConnectionRepository,
        notification_service: NotificationService,
    ) -> None:
        self.disaster_info_client = disaster_info_client
        self.disaster_event_repository = disaster_event_repository
        self.profile_repository = profile_repository
        self.connection_repository = connection_repository
        self.notification_service = notification_service

    def ingest_region(self, region_code: str, now: datetime | None = None) -> DisasterIngestionResult:
        """특정 지역 재난 정보를 수신해 저장하고 긴급 재난 알림을 발송한다."""
        now = now or datetime.now(timezone.utc)
        existing_event_ids = {
            event.event_id
            for event in self.disaster_event_repository.list_active_events(region_code)
        }
        saved_events = self.disaster_info_client.fetch_active_events(region_code)
        emergency_events: list[DisasterEvent] = []
        notified_guardian_user_ids: list[str] = []
        notified_pairs: set[tuple[str, str]] = set()

        for event in saved_events:
            self.disaster_event_repository.save_event(event)
            if event.event_id in existing_event_ids or not self._is_emergency(event, now):
                continue

            emergency_events.append(event)
            for guardian_user_id, protected_user_id in self._notification_targets(event.region_code):
                target_key = (event.event_id, guardian_user_id)
                if target_key in notified_pairs:
                    continue

                self.notification_service.notify_disaster_alert(
                    event=event,
                    protected_user_id=protected_user_id,
                    guardian_user_id=guardian_user_id,
                )
                notified_pairs.add(target_key)
                notified_guardian_user_ids.append(guardian_user_id)

        return DisasterIngestionResult(
            saved_events=saved_events,
            emergency_events=emergency_events,
            notified_guardian_user_ids=notified_guardian_user_ids,
        )

    def _is_emergency(self, event: DisasterEvent, now: datetime) -> bool:
        """지역과 경보 수준 기준으로 긴급 재난 여부를 판단한다."""
        return event.is_active(now) and event.alert_level.strip().lower() in EMERGENCY_ALERT_LEVELS

    def _notification_targets(self, region_code: str) -> list[tuple[str, str]]:
        """지역 내 보호대상자와 연결된 보호자 목록을 반환한다."""
        targets: list[tuple[str, str]] = []
        for profile in self.profile_repository.list_protected_profiles_by_region(region_code):
            connection = self.connection_repository.find_active_by_protected(profile.user_id)
            if connection:
                targets.append((connection.guardian_user_id, profile.user_id))
        return targets
