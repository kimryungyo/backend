"""연결 요청과 활성 연결 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.domain.connection import ConnectionRequest, GuardianProtectedConnection


class ConnectionRepository(ABC):
    """보호자와 보호대상자의 연결 요청 및 활성 연결을 관리한다."""

    @abstractmethod
    def save_request(self, request: ConnectionRequest) -> None:
        """연결 요청을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def get_request(self, request_id: str) -> ConnectionRequest:
        """연결 요청을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def find_active_by_protected(self, protected_user_id: str) -> GuardianProtectedConnection | None:
        """보호대상자의 활성 연결을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def list_active_by_guardian(self, guardian_user_id: str) -> list[GuardianProtectedConnection]:
        """보호자에게 연결된 보호대상자 목록을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def save_connection(self, connection: GuardianProtectedConnection) -> None:
        """수락된 보호자-보호대상자 연결을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def delete_connection_and_related_records(self, connection_id: str) -> None:
        """연결 해제 시 해당 연결과 관련된 기록을 삭제한다."""
        raise NotImplementedError
