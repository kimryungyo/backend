"""위치 요청, 승인, 거절, 30분 미응답 자동 공유 서비스를 정의한다."""

import uuid
from datetime import datetime, timedelta

from app.domain.enums import LocationRequestStatus
from app.domain.location import LocationRequest, LocationShareRecord
from app.external.location_provider_client import LocationProviderClient
from app.repository.connection_repository import ConnectionRepository
from app.repository.location_repository import LocationRepository
from app.repository.profile_repository import ProfileRepository
from app.repository.user_repository import UserRepository
from app.service.notification_service import NotificationService

LOCATION_REQUEST_TIMEOUT_MINUTES = 30


class LocationShareService:
    """위치 요청, 승인, 미응답 자동 공유, 도움 요청 위치 공유를 처리한다."""

    def __init__(
        self,
        profile_repository: ProfileRepository,
        connection_repository: ConnectionRepository,
        user_repository: UserRepository,
        location_repository: LocationRepository,
        location_provider: LocationProviderClient,
        notification_service: NotificationService,
    ) -> None:
        self.profile_repository = profile_repository
        self.connection_repository = connection_repository
        self.user_repository = user_repository
        self.location_repository = location_repository
        self.location_provider = location_provider
        self.notification_service = notification_service

    def request_location(self, guardian_user_id: str, protected_user_id: str, requested_at: datetime) -> LocationRequest:
        """보호자가 보호대상자에게 위치 공유 요청을 보낸다."""
        guardian = self.user_repository.find_by_id(guardian_user_id)
        if not guardian:
            raise ValueError(f"guardian user not found: {guardian_user_id}")
        if not guardian.is_guardian():
            raise ValueError(f"user {guardian_user_id} is not a guardian")

        protected = self.user_repository.find_by_id(protected_user_id)
        if not protected:
            raise ValueError(f"protected user not found: {protected_user_id}")
        if not protected.is_protected():
            raise ValueError(f"user {protected_user_id} is not a protected user")

        connection = self.connection_repository.find_active_by_protected(protected_user_id)
        if not connection or not connection.connects(guardian_user_id, protected_user_id):
            raise ValueError(
                f"active connection not found between guardian {guardian_user_id} "
                f"and protected user {protected_user_id}"
            )

        request = LocationRequest(
            request_id=uuid.uuid4().hex,
            guardian_user_id=guardian_user_id,
            protected_user_id=protected_user_id,
            status=LocationRequestStatus.PENDING,
            requested_at=requested_at,
            expires_at=requested_at + timedelta(minutes=LOCATION_REQUEST_TIMEOUT_MINUTES),
        )
        self.location_repository.save_request(request)
        self.notification_service.notify_location_request(request)
        return request

    def approve_location_request(self, request_id: str, protected_user_id: str) -> LocationShareRecord:
        """보호대상자의 승인 후 현재 위치를 보호자에게 공유한다."""
        request = self.location_repository.get_request(request_id)
        if request.protected_user_id != protected_user_id:
            raise ValueError("위치 요청 대상자가 일치하지 않습니다.")
        if not request.is_pending():
            raise ValueError("대기 중인 위치 요청이 아닙니다.")

        request.approve()
        self.location_repository.save_request(request)

        current_location = self.location_provider.get_current_location(protected_user_id)
        share_record = LocationShareRecord(
            share_id=uuid.uuid4().hex,
            guardian_user_id=request.guardian_user_id,
            protected_user_id=protected_user_id,
            location=current_location,
            reason="approved",
            shared_at=datetime.now(),
        )
        self.location_repository.save_share_record(share_record)
        return share_record

    def reject_location_request(self, request_id: str, protected_user_id: str) -> LocationRequest:
        """보호대상자의 거절 후 위치 요청을 미공유 상태로 처리한다."""
        request = self.location_repository.get_request(request_id)
        if request.protected_user_id != protected_user_id:
            raise ValueError("위치 요청 대상자가 일치하지 않습니다.")
        if not request.is_pending():
            raise ValueError("대기 중인 위치 요청이 아닙니다.")

        request.reject()
        self.location_repository.save_request(request)
        return request

    def auto_share_after_timeout(self, request_id: str, now: datetime) -> LocationShareRecord | None:
        """30분 미응답과 자동 공유 설정을 확인해 위치를 공유한다."""
        raise NotImplementedError

    def share_for_help_request(self, guardian_user_id: str, protected_user_id: str) -> LocationShareRecord:
        """도움 요청 시 현재 위치를 즉시 보호자에게 공유한다."""
        raise NotImplementedError
