"""보호대상자 분류와 위치 자동 공유 설정 변경 서비스를 정의한다."""

from app.domain.enums import ProtectedCategory
from app.domain.profile import ProtectedProfile
from app.repository.profile_repository import ProfileRepository


class ProfileService:
    """보호대상자 분류와 위치 자동 공유 설정을 관리한다."""

    def __init__(self, profile_repository: ProfileRepository) -> None:
        self.profile_repository = profile_repository

    def update_protected_categories(
        self,
        protected_user_id: str,
        categories: list[ProtectedCategory],
        region_code: str,
    ) -> ProtectedProfile:
        """보호대상자가 자신의 재난 대응 특성 분류와 지역 정보를 수정한다."""
        raise NotImplementedError

    def update_auto_location_share(self, protected_user_id: str, enabled: bool) -> ProtectedProfile:
        """보호대상자가 위치 요청 미응답 시 자동 공유 설정을 변경한다."""
        raise NotImplementedError
