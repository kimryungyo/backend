"""보호자와 보호대상자 프로필 도메인 모델을 정의한다."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import ProtectedCategory


@dataclass
class ProtectedProfile:
    """보호대상자의 맞춤 안내와 체크리스트 구성을 위한 정보를 보관한다."""

    user_id: str  # 보호대상자 사용자 ID
    categories: list[ProtectedCategory]  # 고령, 치매, 거동 불편, 청각장애인 등 1차 분류
    region_code: str  # 재난 정보 매칭에 사용할 지역 코드
    auto_location_share_enabled: bool  # 위치 요청 미응답 시 자동 공유 허용 여부
    updated_at: datetime  # 보호대상자 정보가 마지막으로 수정된 시각

    def has_category(self, category: ProtectedCategory) -> bool:
        """보호대상자가 특정 분류에 해당하는지 확인한다."""
        return category in self.categories

    def matches_any_category(self, categories: list[ProtectedCategory]) -> bool:
        """보호대상자가 주어진 분류 목록 중 하나라도 해당하는지 확인한다."""
        return any(category in self.categories for category in categories)

    def can_auto_share_location(self) -> bool:
        """위치 요청 미응답 시 자동 위치 공유를 허용했는지 확인한다."""
        return self.auto_location_share_enabled


@dataclass
class GuardianProfile:
    """보호자의 연결 및 조회 기능에 필요한 정보를 보관한다."""

    user_id: str  # 보호자 사용자 ID
    phone_number: str | None  # 알림 실패 대체 수단 확장에 사용할 수 있는 연락처
    updated_at: datetime  # 보호자 정보가 마지막으로 수정된 시각

    def has_phone_number(self) -> bool:
        """보호자 연락처가 등록되어 있는지 확인한다."""
        return bool(self.phone_number)
