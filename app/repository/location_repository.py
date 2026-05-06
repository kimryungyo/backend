"""위치 요청과 위치 공유 기록 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.domain.location import LocationRequest, LocationShareRecord


class LocationRepository(ABC):
    """위치 요청과 위치 공유 기록을 저장하고 조회한다."""

    @abstractmethod
    def save_request(self, request: LocationRequest) -> None:
        """보호자의 위치 요청을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def get_request(self, request_id: str) -> LocationRequest:
        """위치 요청을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def save_share_record(self, record: LocationShareRecord) -> None:
        """보호자에게 공유된 위치 기록을 저장한다."""
        raise NotImplementedError
