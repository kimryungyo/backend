"""보호대상자 분류와 위치 자동 공유 설정 변경 서비스를 정의한다."""

from datetime import datetime, timezone

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
        try:
            profile = self.profile_repository.get_protected_profile(protected_user_id)
            profile.categories = categories
            profile.region_code = region_code
            profile.updated_at = datetime.now(timezone.utc)
        except (KeyError, IndexError, RuntimeError):
            # 프로필이 존재하지 않는 경우 신규 생성
            profile = ProtectedProfile(
                user_id=protected_user_id,
                categories=categories,
                region_code=region_code,
                auto_location_share_enabled=False,
                updated_at=datetime.now(timezone.utc),
            )

        self.profile_repository.save_protected_profile(profile)
        return profile

    def update_auto_location_share(self, protected_user_id: str, enabled: bool) -> ProtectedProfile:
        """보호대상자가 위치 요청 미응답 시 자동 공유 설정을 변경한다."""
        try:
            profile = self.profile_repository.get_protected_profile(protected_user_id)
            profile.auto_location_share_enabled = enabled
            profile.updated_at = datetime.now(timezone.utc)
        except (KeyError, IndexError, RuntimeError):
            # 프로필이 존재하지 않는 경우 신규 생성
            profile = ProtectedProfile(
                user_id=protected_user_id,
                categories=[],
                region_code="",
                auto_location_share_enabled=enabled,
                updated_at=datetime.now(timezone.utc),
            )

        self.profile_repository.save_protected_profile(profile)
        return profile
