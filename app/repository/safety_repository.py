"""안부 설정과 안부 기록 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod
from datetime import time

from app.database.mysql import MySQLPool
from app.domain.enums import SafetyStatus
from app.domain.safety import SafetyCheckRecord, SafetySchedule


class SafetyRepository(ABC):
    """정기 안부 설정과 안부 확인 기록을 저장하고 조회한다."""

    @abstractmethod
    def save_schedule(self, schedule: SafetySchedule) -> None:
        """보호자가 설정한 정기 안부 확인 규칙을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def get_schedule(self, protected_user_id: str) -> SafetySchedule | None:
        """보호대상자의 정기 안부 확인 규칙을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def save_check_record(self, record: SafetyCheckRecord) -> None:
        """보호대상자의 안부 확인 기록을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def get_latest_check_record(self, protected_user_id: str) -> SafetyCheckRecord | None:
        """보호대상자의 최근 안부 확인 기록을 조회한다."""
        raise NotImplementedError


class MySQLSafetyRepository(SafetyRepository):
    """MySQL 기반 안부 확인 repository 구현체."""

    def __init__(self, mysql_pool: MySQLPool) -> None:
        self._pool = mysql_pool

    def save_schedule(self, schedule: SafetySchedule) -> None:
        """보호자가 설정한 정기 안부 확인 규칙을 저장한다."""
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO safety_schedules
                        (schedule_id, guardian_user_id, protected_user_id, enabled, grace_minutes, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        enabled = VALUES(enabled),
                        grace_minutes = VALUES(grace_minutes),
                        updated_at = VALUES(updated_at)
                    """,
                    (
                        schedule.schedule_id,
                        schedule.guardian_user_id,
                        schedule.protected_user_id,
                        int(schedule.enabled),
                        schedule.grace_minutes,
                        schedule.updated_at,
                    ),
                )
                cursor.execute(
                    "DELETE FROM safety_schedule_times WHERE schedule_id = %s",
                    (schedule.schedule_id,),
                )
                if schedule.check_times:
                    cursor.executemany(
                        "INSERT INTO safety_schedule_times (schedule_id, check_time) VALUES (%s, %s)",
                        [(schedule.schedule_id, t.strftime("%H:%M:%S")) for t in schedule.check_times],
                    )
            finally:
                cursor.close()

    def get_schedule(self, protected_user_id: str) -> SafetySchedule | None:
        """보호대상자의 정기 안부 확인 규칙을 조회한다."""
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT schedule_id, guardian_user_id, protected_user_id, enabled, grace_minutes, updated_at
                FROM safety_schedules WHERE protected_user_id = %s
                ORDER BY updated_at DESC LIMIT 1
                """,
                (protected_user_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            cursor.execute(
                "SELECT check_time FROM safety_schedule_times WHERE schedule_id = %s",
                (row["schedule_id"],),
            )
            check_times = [
                (t["check_time"] if isinstance(t["check_time"], time) else _timedelta_to_time(t["check_time"]))
                for t in cursor.fetchall()
            ]

        return SafetySchedule(
            schedule_id=row["schedule_id"],
            guardian_user_id=row["guardian_user_id"],
            protected_user_id=row["protected_user_id"],
            enabled=bool(row["enabled"]),
            check_times=check_times,
            grace_minutes=row["grace_minutes"],
            updated_at=row["updated_at"],
        )

    def save_check_record(self, record: SafetyCheckRecord) -> None:
        """보호대상자의 안부 확인 기록을 저장한다."""
        sql = """
            INSERT INTO safety_check_records (record_id, protected_user_id, status, checked_at)
            VALUES (%s, %s, %s, %s)
        """
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (
                    record.record_id,
                    record.protected_user_id,
                    record.status.value,
                    record.checked_at,
                ))
            finally:
                cursor.close()

    def get_latest_check_record(self, protected_user_id: str) -> SafetyCheckRecord | None:
        """보호대상자의 최근 안부 확인 기록을 조회한다."""
        sql = """
            SELECT record_id, protected_user_id, status, checked_at
            FROM safety_check_records WHERE protected_user_id = %s
            ORDER BY checked_at DESC LIMIT 1
        """
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(sql, (protected_user_id,))
            row = cursor.fetchone()
        if row is None:
            return None
        return SafetyCheckRecord(
            record_id=row["record_id"],
            protected_user_id=row["protected_user_id"],
            status=SafetyStatus(row["status"]),
            checked_at=row["checked_at"],
        )


def _timedelta_to_time(td: object) -> time:
    """MySQL TIME 컬럼이 timedelta로 반환될 때 time 객체로 변환한다."""
    import datetime as _dt
    total_seconds = int(td.total_seconds())  # type: ignore[union-attr]
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return _dt.time(hours % 24, minutes, seconds)
