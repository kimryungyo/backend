"""연결 요청과 활성 연결 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.database.mysql import MySQLPool
from app.domain.connection import ConnectionRequest, GuardianProtectedConnection
from app.domain.enums import ConnectionRequestStatus


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
    def get_connection(self, connection_id: str) -> GuardianProtectedConnection:
        """활성 연결을 조회한다."""
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


class MySQLConnectionRepository(ConnectionRepository):
    """MySQL 기반 연결 repository 구현체."""

    def __init__(self, mysql_pool: MySQLPool) -> None:
        self._pool = mysql_pool

    def _to_request(self, row: dict) -> ConnectionRequest:
        return ConnectionRequest(
            request_id=row["request_id"],
            requester_user_id=row["requester_user_id"],
            target_user_id=row["target_user_id"],
            status=ConnectionRequestStatus(row["status"]),
            created_at=row["created_at"],
            responded_at=row["responded_at"],
        )

    def _to_connection(self, row: dict) -> GuardianProtectedConnection:
        return GuardianProtectedConnection(
            connection_id=row["connection_id"],
            guardian_user_id=row["guardian_user_id"],
            protected_user_id=row["protected_user_id"],
            created_at=row["created_at"],
        )

    def save_request(self, request: ConnectionRequest) -> None:
        """연결 요청을 저장한다."""
        sql = """
            INSERT INTO connection_requests
                (request_id, requester_user_id, target_user_id, status, created_at, responded_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status = VALUES(status),
                responded_at = VALUES(responded_at)
        """
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (
                    request.request_id,
                    request.requester_user_id,
                    request.target_user_id,
                    request.status.value,
                    request.created_at,
                    request.responded_at,
                ))
            finally:
                cursor.close()

    def get_request(self, request_id: str) -> ConnectionRequest:
        """연결 요청을 조회한다."""
        sql = """
            SELECT request_id, requester_user_id, target_user_id, status, created_at, responded_at
            FROM connection_requests WHERE request_id = %s
        """
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(sql, (request_id,))
            row = cursor.fetchone()
        if row is None:
            raise KeyError(request_id)
        return self._to_request(row)

    def find_active_by_protected(self, protected_user_id: str) -> GuardianProtectedConnection | None:
        """보호대상자의 활성 연결을 조회한다."""
        sql = """
            SELECT connection_id, guardian_user_id, protected_user_id, created_at
            FROM guardian_protected_connections WHERE protected_user_id = %s
        """
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(sql, (protected_user_id,))
            row = cursor.fetchone()
        return self._to_connection(row) if row else None

    def list_active_by_guardian(self, guardian_user_id: str) -> list[GuardianProtectedConnection]:
        """보호자에게 연결된 보호대상자 목록을 조회한다."""
        sql = """
            SELECT connection_id, guardian_user_id, protected_user_id, created_at
            FROM guardian_protected_connections WHERE guardian_user_id = %s
        """
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(sql, (guardian_user_id,))
            rows = cursor.fetchall()
        return [self._to_connection(row) for row in rows]

    def save_connection(self, connection: GuardianProtectedConnection) -> None:
        """수락된 보호자-보호대상자 연결을 저장한다."""
        sql = """
            INSERT INTO guardian_protected_connections
                (connection_id, guardian_user_id, protected_user_id, created_at)
            VALUES (%s, %s, %s, %s)
        """
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (
                    connection.connection_id,
                    connection.guardian_user_id,
                    connection.protected_user_id,
                    connection.created_at,
                ))
            finally:
                cursor.close()

    def delete_connection_and_related_records(self, connection_id: str) -> None:
        """연결 해제 시 해당 연결과 관련된 기록을 삭제한다."""
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "DELETE FROM guardian_protected_connections WHERE connection_id = %s",
                    (connection_id,),
                )
            finally:
                cursor.close()
