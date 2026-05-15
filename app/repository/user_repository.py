"""사용자 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.database.mysql import MySQLPool
from app.domain.enums import UserRole
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


class MySQLUserRepository(UserRepository):
    """MySQL 기반 사용자 repository 구현체."""

    _SELECT = "SELECT user_id, kakao_id, role, connection_code, name, created_at FROM users"

    def __init__(self, mysql_pool: MySQLPool) -> None:
        self._pool = mysql_pool

    def _to_user(self, row: dict) -> User:
        return User(
            user_id=row["user_id"],
            kakao_id=row["kakao_id"],
            role=UserRole(row["role"]),
            connection_code=row["connection_code"],
            name=row["name"],
            created_at=row["created_at"],
        )

    def find_by_id(self, user_id: str) -> User | None:
        """시스템 내부 사용자 ID로 가입 사용자를 조회한다."""
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(f"{self._SELECT} WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
        return self._to_user(row) if row else None

    def find_by_kakao_id(self, kakao_id: str) -> User | None:
        """카카오 사용자 식별자로 가입 사용자를 조회한다."""
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(f"{self._SELECT} WHERE kakao_id = %s", (kakao_id,))
            row = cursor.fetchone()
        return self._to_user(row) if row else None

    def find_by_connection_code(self, connection_code: str) -> User | None:
        """6자리 연결 아이디로 사용자를 조회한다."""
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(f"{self._SELECT} WHERE connection_code = %s", (connection_code,))
            row = cursor.fetchone()
        return self._to_user(row) if row else None

    def save(self, user: User) -> None:
        """사용자 계정을 저장한다."""
        sql = """
            INSERT INTO users (user_id, kakao_id, role, connection_code, name, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                kakao_id = VALUES(kakao_id),
                role = VALUES(role),
                connection_code = VALUES(connection_code),
                name = VALUES(name)
        """
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (
                    user.user_id,
                    user.kakao_id,
                    user.role.value,
                    user.connection_code,
                    user.name,
                    user.created_at,
                ))
            finally:
                cursor.close()
