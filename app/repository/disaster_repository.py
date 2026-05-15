"""재난 이벤트와 재난 카탈로그 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

from app.database.mysql import MySQLPool
from app.domain.disaster import DisasterCatalog, DisasterEvent


class DisasterCatalogRepository(ABC):
    """JSON 기반 재난 카탈로그를 로드하고 저장한다."""

    @abstractmethod
    def load_catalog(self, source_path: Path) -> DisasterCatalog:
        """JSON 파일에서 재난 정의, 체크리스트, 대처법 안내를 읽어온다."""
        raise NotImplementedError

    @abstractmethod
    def save_catalog(self, catalog: DisasterCatalog, target_path: Path) -> None:
        """재난 카탈로그를 JSON 파일로 저장한다."""
        raise NotImplementedError


class DisasterEventRepository(ABC):
    """외부 API에서 수신한 재난 상황을 저장하고 조회한다."""

    @abstractmethod
    def save_event(self, event: DisasterEvent) -> None:
        """재난 상황 정보를 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def list_active_events(self, region_code: str) -> list[DisasterEvent]:
        """특정 지역에 적용 중인 재난 상황 목록을 조회한다."""
        raise NotImplementedError


class MySQLDisasterEventRepository(DisasterEventRepository):
    """MySQL 기반 재난 이벤트 repository 구현체."""

    def __init__(self, mysql_pool: MySQLPool) -> None:
        self._pool = mysql_pool

    def _to_event(self, row: dict) -> DisasterEvent:
        return DisasterEvent(
            event_id=row["event_id"],
            disaster_type=row["disaster_type"],
            region_code=row["region_code"],
            alert_level=row["alert_level"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
        )

    def save_event(self, event: DisasterEvent) -> None:
        """재난 상황 정보를 저장한다."""
        sql = """
            INSERT INTO disaster_events
                (event_id, disaster_type, region_code, alert_level, started_at, ended_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                alert_level = VALUES(alert_level),
                ended_at = VALUES(ended_at)
        """
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (
                    event.event_id,
                    event.disaster_type,
                    event.region_code,
                    event.alert_level,
                    event.started_at,
                    event.ended_at,
                ))
            finally:
                cursor.close()

    def list_active_events(self, region_code: str) -> list[DisasterEvent]:
        """특정 지역에 적용 중인 재난 상황 목록을 조회한다."""
        now = datetime.now(timezone.utc)
        sql = """
            SELECT event_id, disaster_type, region_code, alert_level, started_at, ended_at
            FROM disaster_events
            WHERE region_code = %s
              AND started_at <= %s
              AND (ended_at IS NULL OR ended_at >= %s)
        """
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(sql, (region_code, now, now))
            rows = cursor.fetchall()
        return [self._to_event(row) for row in rows]
