"""도움 요청 도메인 모델을 정의한다."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class HelpRequestRecord:
    """보호대상자가 보호자에게 도움을 요청한 기록을 나타낸다."""

    request_id: str  # 도움 요청 ID
    protected_user_id: str  # 도움을 요청한 보호대상자 사용자 ID
    guardian_user_id: str  # 도움 요청을 받을 보호자 사용자 ID
    location_share_id: str  # 도움 요청과 함께 공유된 위치 기록 ID
    requested_at: datetime  # 도움 요청 시각

    def includes_location(self) -> bool:
        """도움 요청에 위치 공유 기록이 연결되어 있는지 확인한다."""
        return bool(self.location_share_id)
