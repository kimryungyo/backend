"""체크리스트 수행 기록 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.database.mysql import MySQLPool
from app.domain.checklist import ChecklistRecord


class ChecklistRepository(ABC):
    """재난 체크리스트 수행 기록을 저장하고 조회한다."""

    @abstractmethod
    def save_record(self, record: ChecklistRecord) -> None:
        """체크리스트 수행 기록을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def list_recent_records(self, protected_user_id: str, limit: int = 3) -> list[ChecklistRecord]:
        """보호자의 조회를 위해 최근 재난 체크리스트 기록을 조회한다."""
        raise NotImplementedError


class MySQLChecklistRepository(ChecklistRepository):
    """MySQL 기반 체크리스트 수행 기록 repository 구현체."""

    def __init__(self, mysql_pool: MySQLPool) -> None:
        self._pool = mysql_pool

    def save_record(self, record: ChecklistRecord) -> None:
        """체크리스트 수행 기록을 저장한다."""
        sql = """
            INSERT INTO checklist_records
                (record_id, protected_user_id, disaster_event_id, checklist_rule_id, completed_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (
                    record.record_id,
                    record.protected_user_id,
                    record.disaster_event_id,
                    record.checklist_rule_id,
                    record.completed_at,
                ))
            finally:
                cursor.close()

    def list_recent_records(self, protected_user_id: str, limit: int = 3) -> list[ChecklistRecord]:
        """보호자의 조회를 위해 최근 재난 체크리스트 기록을 조회한다."""
        sql = """
            SELECT record_id, protected_user_id, disaster_event_id, checklist_rule_id, completed_at
            FROM checklist_records
            WHERE protected_user_id = %s
            ORDER BY completed_at DESC
            LIMIT %s
        """
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(sql, (protected_user_id, limit))
            rows = cursor.fetchall()

        return [
            ChecklistRecord(
                record_id=row["record_id"],
                protected_user_id=row["protected_user_id"],
                disaster_event_id=row["disaster_event_id"],
                checklist_rule_id=row["checklist_rule_id"],
                completed_at=row["completed_at"],
            )
            for row in rows
        ]
