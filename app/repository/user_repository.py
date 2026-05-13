"""사용자 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.domain.user import User


class UserRepository(ABC):
    """사용자 계정과 역할 정보를 저장하고 조회한다."""

    @abstractmethod
    def find_by_id(self, user_id: str) -> User | None:
        """시스템 내부 사용자 ID로 가입 사용자를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def find_by_kakao_id(self, kakao_id: str) -> User | None:
        """카카오 사용자 식별자로 가입 사용자를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def find_by_connection_code(self, connection_code: str) -> User | None:
        """6자리 연결 아이디로 사용자를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def save(self, user: User) -> None:
        """사용자 계정을 저장한다."""
        raise NotImplementedError
