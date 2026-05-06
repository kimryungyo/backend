"""외부 재난 정보 API 연동 클라이언트를 정의한다."""

from app.domain.disaster import DisasterEvent


class DisasterInfoClient:
    """외부 재난 정보 API에서 재난 상황 정보를 수신한다."""

    def fetch_active_events(self, region_code: str) -> list[DisasterEvent]:
        """특정 지역의 현재 재난 상황 목록을 조회한다."""
        raise NotImplementedError
