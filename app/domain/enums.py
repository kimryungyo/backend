"""서비스 전반에서 공유하는 enum 값을 정의한다."""

from enum import Enum


class UserRole(str, Enum):
    """가입 시 선택하는 사용자 역할을 나타낸다."""

    GUARDIAN = "guardian"
    PROTECTED = "protected"


class ProtectedCategory(str, Enum):
    """보호대상자의 재난 대응 특성 분류를 나타낸다."""

    ELDERLY = "elderly"
    DEMENTIA = "dementia"
    MOBILITY_LIMITED = "mobility_limited"
    HEARING_IMPAIRED = "hearing_impaired"


class ConnectionRequestStatus(str, Enum):
    """보호자와 보호대상자 연결 요청 상태를 나타낸다."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELED = "canceled"


class SafetyStatus(str, Enum):
    """안부 확인 상태를 나타낸다."""

    SAFE = "safe"
    NOT_RESPONDED = "not_responded"
    HELP_REQUESTED = "help_requested"


class LocationRequestStatus(str, Enum):
    """위치 요청 처리 상태를 나타낸다."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_SHARED = "auto_shared"
    EXPIRED = "expired"


class NotificationType(str, Enum):
    """서비스에서 전송하는 알림 종류를 나타낸다."""

    CONNECTION_REQUEST = "connection_request"
    SAFETY_CHECK_REQUEST = "safety_check_request"
    SAFETY_NOT_RESPONDED = "safety_not_responded"
    CHECKLIST_NOT_DONE = "checklist_not_done"
    HELP_REQUEST = "help_request"
    LOCATION_REQUEST = "location_request"
    DISASTER_ALERT = "disaster_alert"
