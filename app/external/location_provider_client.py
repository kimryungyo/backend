"""현재 위치 조회 연동 클라이언트를 정의한다."""

from app.domain.location import GeoLocation


class LocationProviderClient:
    """보호대상자 기기 또는 위치 정보 서비스에서 현재 위치를 가져온다."""

    def get_current_location(self, protected_user_id: str) -> GeoLocation:
        """보호대상자의 현재 위치 정보를 조회한다."""
        raise NotImplementedError
