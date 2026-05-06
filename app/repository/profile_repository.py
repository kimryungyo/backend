"""보호자와 보호대상자 프로필 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.domain.profile import GuardianProfile, ProtectedProfile


class ProfileRepository(ABC):
    """보호자와 보호대상자의 프로필 정보를 저장하고 조회한다."""

    @abstractmethod
    def get_protected_profile(self, user_id: str) -> ProtectedProfile:
        """보호대상자 프로필을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def save_protected_profile(self, profile: ProtectedProfile) -> None:
        """보호대상자 프로필을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def get_guardian_profile(self, user_id: str) -> GuardianProfile:
        """보호자 프로필을 조회한다."""
        raise NotImplementedError
