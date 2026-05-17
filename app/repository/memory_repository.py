"""개발 및 테스트용 메모리 기반 repository 구현체를 정의한다."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.domain.action_guide import ActionGuidePage, ActionGuideRule
from app.domain.checklist import ChecklistRecord, ChecklistRule
from app.domain.connection import ConnectionRequest, GuardianProtectedConnection
from app.domain.disaster import DisasterCatalog, DisasterDefinition, DisasterEvent
from app.domain.enums import ProtectedCategory
from app.domain.location import LocationRequest, LocationShareRecord
from app.domain.notification import NotificationMessage
from app.domain.profile import GuardianProfile, ProtectedProfile
from app.domain.safety import SafetyCheckRecord, SafetySchedule
from app.domain.user import User
from app.repository.checklist_repository import ChecklistRepository
from app.repository.connection_repository import ConnectionRepository
from app.repository.disaster_repository import DisasterCatalogRepository, DisasterEventRepository
from app.repository.location_repository import LocationRepository
from app.repository.notification_repository import NotificationRepository
from app.repository.profile_repository import ProfileRepository
from app.repository.safety_repository import SafetyRepository
from app.repository.user_repository import UserRepository


def _parse_datetime(value: str) -> datetime:
    """ISO 8601 문자열을 datetime으로 변환한다."""
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class JsonDisasterCatalogRepository(DisasterCatalogRepository):
    """JSON 파일 기반 재난 카탈로그 repository 구현체."""

    def load_catalog(self, source_path: Path) -> DisasterCatalog:
        """JSON 파일에서 재난 정의, 체크리스트, 대처법 안내를 읽어온다."""
        with source_path.open(encoding="utf-8") as file:
            payload = json.load(file)

        disasters = [
            self._parse_disaster_definition(disaster_payload)
            for disaster_payload in payload.get("disasters", [])
        ]
        return DisasterCatalog(
            version=payload["version"],
            updated_at=_parse_datetime(payload["updated_at"]),
            disasters=disasters,
        )

    def save_catalog(self, catalog: DisasterCatalog, target_path: Path) -> None:
        """재난 카탈로그를 JSON 파일로 저장한다."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open("w", encoding="utf-8") as file:
            json.dump(self._serialize_catalog(catalog), file, ensure_ascii=False, indent=2)
            file.write("\n")

    def _parse_disaster_definition(self, payload: dict[str, Any]) -> DisasterDefinition:
        disaster_type = payload["disaster_type"]
        checklist_rules = [
            ChecklistRule(
                rule_id=rule_payload["rule_id"],
                disaster_type=disaster_type,
                category=ProtectedCategory(rule_payload["category"]),
                title=rule_payload["title"],
                interval_minutes=rule_payload["interval_minutes"],
                enabled=rule_payload["enabled"],
            )
            for rule_payload in payload.get("checklist_rules", [])
        ]
        guide_rules = [
            ActionGuideRule(
                guide_id=guide_payload["guide_id"],
                disaster_type=disaster_type,
                category=ProtectedCategory(guide_payload["category"]),
                enabled=guide_payload["enabled"],
                pages=[
                    ActionGuidePage(
                        page_no=page_payload["page_no"],
                        text=page_payload["text"],
                        image_url=page_payload.get("image_url"),
                    )
                    for page_payload in guide_payload.get("pages", [])
                ],
            )
            for guide_payload in payload.get("guide_rules", [])
        ]
        return DisasterDefinition(
            disaster_type=disaster_type,
            display_name=payload["display_name"],
            checklist_rules=checklist_rules,
            guide_rules=guide_rules,
        )

    def _serialize_catalog(self, catalog: DisasterCatalog) -> dict[str, Any]:
        return {
            "version": catalog.version,
            "updated_at": catalog.updated_at.isoformat(),
            "disasters": [
                {
                    "disaster_type": disaster.disaster_type,
                    "display_name": disaster.display_name,
                    "checklist_rules": [
                        {
                            "rule_id": rule.rule_id,
                            "category": rule.category.value,
                            "title": rule.title,
                            "interval_minutes": rule.interval_minutes,
                            "enabled": rule.enabled,
                        }
                        for rule in disaster.checklist_rules
                    ],
                    "guide_rules": [
                        {
                            "guide_id": guide.guide_id,
                            "category": guide.category.value,
                            "enabled": guide.enabled,
                            "pages": [
                                {
                                    "page_no": page.page_no,
                                    "text": page.text,
                                    "image_url": page.image_url,
                                }
                                for page in guide.ordered_pages()
                            ],
                        }
                        for guide in disaster.guide_rules
                    ],
                }
                for disaster in catalog.disasters
            ],
        }


class InMemoryDisasterEventRepository(DisasterEventRepository):
    """메모리 기반 재난 이벤트 repository 구현체."""

    def __init__(self) -> None:
        self._events: dict[str, DisasterEvent] = {}

    def save_event(self, event: DisasterEvent) -> None:
        """재난 상황 정보를 저장한다."""
        self._events[event.event_id] = event

    def list_active_events(self, region_code: str) -> list[DisasterEvent]:
        """특정 지역에 적용 중인 재난 상황 목록을 조회한다."""
        active_events = []
        for event in self._events.values():
            now = datetime.now(tz=event.started_at.tzinfo)
            if event.affects_region(region_code) and event.is_active(now):
                active_events.append(event)
        return active_events


class InMemoryUserRepository(UserRepository):
    """메모리 기반 사용자 repository 구현체."""

    def __init__(self) -> None:
        self._users_by_id: dict[str, User] = {}

    def find_by_id(self, user_id: str) -> User | None:
        """시스템 내부 사용자 ID로 가입 사용자를 조회한다."""
        return self._users_by_id.get(user_id)

    def find_by_kakao_id(self, kakao_id: str) -> User | None:
        """카카오 사용자 식별자로 가입 사용자를 조회한다."""
        return next((user for user in self._users_by_id.values() if user.kakao_id == kakao_id), None)

    def find_by_connection_code(self, connection_code: str) -> User | None:
        """6자리 연결 아이디로 사용자를 조회한다."""
        return next(
            (user for user in self._users_by_id.values() if user.connection_code == connection_code),
            None,
        )

    def save(self, user: User) -> None:
        """사용자 계정을 저장한다."""
        self._users_by_id[user.user_id] = user


class InMemoryProfileRepository(ProfileRepository):
    """메모리 기반 프로필 repository 구현체."""

    def __init__(self) -> None:
        self._protected_profiles: dict[str, ProtectedProfile] = {}
        self._guardian_profiles: dict[str, GuardianProfile] = {}

    def get_protected_profile(self, user_id: str) -> ProtectedProfile:
        """보호대상자 프로필을 조회한다."""
        return self._protected_profiles[user_id]

    def save_protected_profile(self, profile: ProtectedProfile) -> None:
        """보호대상자 프로필을 저장한다."""
        self._protected_profiles[profile.user_id] = profile

    def get_guardian_profile(self, user_id: str) -> GuardianProfile:
        """보호자 프로필을 조회한다."""
        return self._guardian_profiles[user_id]

    def save_guardian_profile(self, profile: GuardianProfile) -> None:
        """보호자 프로필을 저장한다."""
        self._guardian_profiles[profile.user_id] = profile


class InMemoryConnectionRepository(ConnectionRepository):
    """메모리 기반 연결 repository 구현체."""

    def __init__(self) -> None:
        self._requests: dict[str, ConnectionRequest] = {}
        self._connections: dict[str, GuardianProtectedConnection] = {}

    def save_request(self, request: ConnectionRequest) -> None:
        """연결 요청을 저장한다."""
        self._requests[request.request_id] = request

    def get_request(self, request_id: str) -> ConnectionRequest:
        """연결 요청을 조회한다."""
        return self._requests[request_id]

    def get_connection(self, connection_id: str) -> GuardianProtectedConnection:
        """활성 연결을 조회한다."""
        return self._connections[connection_id]

    def find_active_by_protected(self, protected_user_id: str) -> GuardianProtectedConnection | None:
        """보호대상자의 활성 연결을 조회한다."""
        return next(
            (
                connection
                for connection in self._connections.values()
                if connection.protected_user_id == protected_user_id
            ),
            None,
        )

    def list_active_by_guardian(self, guardian_user_id: str) -> list[GuardianProtectedConnection]:
        """보호자에게 연결된 보호대상자 목록을 조회한다."""
        return [
            connection
            for connection in self._connections.values()
            if connection.guardian_user_id == guardian_user_id
        ]

    def save_connection(self, connection: GuardianProtectedConnection) -> None:
        """수락된 보호자-보호대상자 연결을 저장한다."""
        self._connections[connection.connection_id] = connection

    def delete_connection_and_related_records(self, connection_id: str) -> None:
        """연결 해제 시 해당 연결과 관련된 기록을 삭제한다."""
        self._connections.pop(connection_id, None)


class InMemorySafetyRepository(SafetyRepository):
    """메모리 기반 안부 확인 repository 구현체."""

    def __init__(self) -> None:
        self._schedules_by_protected_id: dict[str, SafetySchedule] = {}
        self._check_records: list[SafetyCheckRecord] = []

    def save_schedule(self, schedule: SafetySchedule) -> None:
        """보호자가 설정한 정기 안부 확인 규칙을 저장한다."""
        self._schedules_by_protected_id[schedule.protected_user_id] = schedule

    def get_schedule(self, protected_user_id: str) -> SafetySchedule | None:
        """보호대상자의 정기 안부 확인 규칙을 조회한다."""
        return self._schedules_by_protected_id.get(protected_user_id)

    def save_check_record(self, record: SafetyCheckRecord) -> None:
        """보호대상자의 안부 확인 기록을 저장한다."""
        self._check_records.append(record)

    def get_latest_check_record(self, protected_user_id: str) -> SafetyCheckRecord | None:
        """보호대상자의 최근 안부 확인 기록을 조회한다."""
        records = [record for record in self._check_records if record.protected_user_id == protected_user_id]
        return max(records, key=lambda record: record.checked_at, default=None)


class InMemoryChecklistRepository(ChecklistRepository):
    """메모리 기반 체크리스트 repository 구현체."""

    def __init__(self) -> None:
        self._records: list[ChecklistRecord] = []

    def save_record(self, record: ChecklistRecord) -> None:
        """체크리스트 수행 기록을 저장한다."""
        self._records.append(record)

    def list_recent_records(self, protected_user_id: str, limit: int = 3) -> list[ChecklistRecord]:
        """보호자의 조회를 위해 최근 재난 체크리스트 기록을 조회한다."""
        records = [record for record in self._records if record.protected_user_id == protected_user_id]
        return sorted(records, key=lambda record: record.completed_at, reverse=True)[:limit]


class InMemoryLocationRepository(LocationRepository):
    """메모리 기반 위치 repository 구현체."""

    def __init__(self) -> None:
        self._requests: dict[str, LocationRequest] = {}
        self._share_records: dict[str, LocationShareRecord] = {}

    def save_request(self, request: LocationRequest) -> None:
        """보호자의 위치 요청을 저장한다."""
        self._requests[request.request_id] = request

    def get_request(self, request_id: str) -> LocationRequest:
        """위치 요청을 조회한다."""
        return self._requests[request_id]

    def save_share_record(self, record: LocationShareRecord) -> None:
        """보호자에게 공유된 위치 기록을 저장한다."""
        self._share_records[record.share_id] = record


class InMemoryNotificationRepository(NotificationRepository):
    """메모리 기반 알림 repository 구현체."""

    def __init__(self) -> None:
        self._messages: dict[str, NotificationMessage] = {}

    def save(self, message: NotificationMessage) -> None:
        """알림 메시지와 전송 상태를 저장한다."""
        self._messages[message.notification_id] = message
