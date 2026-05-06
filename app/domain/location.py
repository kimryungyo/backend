"""위치 요청과 위치 공유 도메인 모델을 정의한다."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import LocationRequestStatus


@dataclass
class GeoLocation:
    """보호대상자의 현재 위치 정보를 나타낸다."""

    latitude: float  # 위도
    longitude: float  # 경도
    accuracy_meters: float | None  # 위치 정확도
    address: str | None  # 화면 표시용 주소
    captured_at: datetime  # 위치가 확인된 시각

    def has_accuracy(self) -> bool:
        """위치 정확도 정보가 포함되어 있는지 확인한다."""
        return self.accuracy_meters is not None

    def is_accurate_enough(self, max_accuracy_meters: float) -> bool:
        """위치 정확도가 허용 범위 안인지 확인한다."""
        return self.accuracy_meters is not None and self.accuracy_meters <= max_accuracy_meters


@dataclass
class LocationRequest:
    """보호자가 보호대상자에게 보낸 위치 공유 요청을 나타낸다."""

    request_id: str  # 위치 요청 ID
    guardian_user_id: str  # 위치를 요청한 보호자 사용자 ID
    protected_user_id: str  # 위치 공유 대상 보호대상자 사용자 ID
    status: LocationRequestStatus  # 승인, 거절, 자동 공유, 만료 상태
    requested_at: datetime  # 위치 요청 생성 시각
    expires_at: datetime  # 미응답 자동 공유 판단 시각

    def is_pending(self) -> bool:
        """위치 요청이 아직 응답 대기 상태인지 확인한다."""
        return self.status == LocationRequestStatus.PENDING

    def is_expired(self, now: datetime) -> bool:
        """현재 시각 기준 위치 요청 미응답 시간이 지났는지 확인한다."""
        return self.is_pending() and now >= self.expires_at

    def approve(self) -> None:
        """위치 요청을 승인 상태로 변경한다."""
        self.status = LocationRequestStatus.APPROVED

    def reject(self) -> None:
        """위치 요청을 거절 상태로 변경한다."""
        self.status = LocationRequestStatus.REJECTED

    def mark_auto_shared(self) -> None:
        """위치 요청을 미응답 자동 공유 상태로 변경한다."""
        self.status = LocationRequestStatus.AUTO_SHARED

    def expire(self) -> None:
        """위치 요청을 만료 상태로 변경한다."""
        self.status = LocationRequestStatus.EXPIRED


@dataclass
class LocationShareRecord:
    """조건을 만족해 보호자에게 위치가 공유된 기록을 나타낸다."""

    share_id: str  # 위치 공유 기록 ID
    guardian_user_id: str  # 위치를 확인한 보호자 사용자 ID
    protected_user_id: str  # 위치를 공유한 보호대상자 사용자 ID
    location: GeoLocation  # 공유된 현재 위치
    reason: str  # 승인, 미응답 자동 공유, 도움 요청 등 공유 사유
    shared_at: datetime  # 위치가 보호자에게 공유된 시각

    def was_shared_for_help_request(self) -> bool:
        """도움 요청 때문에 위치가 공유된 기록인지 확인한다."""
        return self.reason == "help_request"
