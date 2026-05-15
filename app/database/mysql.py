"""MySQL connection pool 헬퍼를 정의한다."""

from collections.abc import Iterator
from contextlib import contextmanager
from queue import Empty
from typing import Any

from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection

from app.config.settings import Settings


class MySQLPool:
    """Settings 값을 기반으로 MySQL connection pool을 지연 생성한다."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pool: MySQLConnectionPool | None = None

    @property
    def pool(self) -> MySQLConnectionPool:
        """connection pool을 반환하고, 아직 없으면 최초 1회 생성한다."""
        if self._pool is None:
            self._pool = MySQLConnectionPool(
                pool_name=self._settings.mysql_pool_name,
                pool_size=self._settings.mysql_pool_size,
                pool_reset_session=True,
                host=self._settings.mysql_host,
                port=self._settings.mysql_port,
                user=self._settings.mysql_user,
                password=self._settings.mysql_password,
                database=self._settings.mysql_database,
                charset=self._settings.mysql_charset,
                autocommit=self._settings.mysql_autocommit,
                connection_timeout=self._settings.mysql_connection_timeout_seconds,
            )
        return self._pool

    def get_connection(self) -> PooledMySQLConnection:
        """pool에서 connection을 하나 가져온다."""
        return self.pool.get_connection()

    def initialize(self) -> None:
        """애플리케이션 시작 시 connection pool을 미리 생성한다."""
        _ = self.pool

    def close(self) -> None:
        """pool 내부의 유휴 connection을 종료한다."""
        if self._pool is None:
            return

        while True:
            try:
                connection = self._pool._cnx_queue.get(block=False)  # noqa: SLF001
            except Empty:
                break
            connection.close()
        self._pool = None

    @contextmanager
    def connection(self) -> Iterator[PooledMySQLConnection]:
        """with 블록 종료 시 connection을 pool에 반환한다."""
        connection = self.get_connection()
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def cursor(self, *, dictionary: bool = False, buffered: bool = False) -> Iterator[Any]:
        """쿼리 실행용 cursor를 열고, 사용 후 cursor와 connection을 정리한다."""
        with self.connection() as connection:
            cursor = connection.cursor(dictionary=dictionary, buffered=buffered)
            try:
                yield cursor
            finally:
                cursor.close()

    @contextmanager
    def transaction(self) -> Iterator[PooledMySQLConnection]:
        """예외 발생 시 rollback, 정상 종료 시 commit하는 transaction context를 제공한다."""
        with self.connection() as connection:
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise
            else:
                connection.commit()
