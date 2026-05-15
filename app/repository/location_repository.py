"""위치 요청과 위치 공유 기록 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.database.mysql import MySQLPool
from app.domain.enums import LocationRequestStatus
from app.domain.location import GeoLocation, LocationRequest, LocationShareRecord


class LocationRepository(ABC):
    """위치 요청과 위치 공유 기록을 저장하고 조회한다."""

    @abstractmethod
    def save_request(self, request: LocationRequest) -> None:
        """보호자의 위치 요청을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def get_request(self, request_id: str) -> LocationRequest:
        """위치 요청을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def save_share_record(self, record: LocationShareRecord) -> None:
        """보호자에게 공유된 위치 기록을 저장한다."""
        raise NotImplementedError


class MySQLLocationRepository(LocationRepository):
    """MySQL 기반 위치 요청 및 공유 기록 repository 구현체."""

    def __init__(self, mysql_pool: MySQLPool) -> None:
        self._pool = mysql_pool

    def save_request(self, request: LocationRequest) -> None:
        """보호자의 위치 요청을 저장한다."""
        sql = """
            INSERT INTO location_requests
                (request_id, guardian_user_id, protected_user_id, status, requested_at, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status = VALUES(status)
        """
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (
                    request.request_id,
                    request.guardian_user_id,
                    request.protected_user_id,
                    request.status.value,
                    request.requested_at,
                    request.expires_at,
                ))
            finally:
                cursor.close()

    def get_request(self, request_id: str) -> LocationRequest:
        """위치 요청을 조회한다."""
        sql = """
            SELECT request_id, guardian_user_id, protected_user_id, status, requested_at, expires_at
            FROM location_requests WHERE request_id = %s
        """
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(sql, (request_id,))
            row = cursor.fetchone()
        if row is None:
            raise KeyError(request_id)
        return LocationRequest(
            request_id=row["request_id"],
            guardian_user_id=row["guardian_user_id"],
            protected_user_id=row["protected_user_id"],
            status=LocationRequestStatus(row["status"]),
            requested_at=row["requested_at"],
            expires_at=row["expires_at"],
        )

    def save_share_record(self, record: LocationShareRecord) -> None:
        """보호자에게 공유된 위치 기록을 저장한다."""
        sql = """
            INSERT INTO location_share_records (
                share_id, guardian_user_id, protected_user_id, reason, shared_at,
                latitude, longitude, accuracy_meters, address, captured_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        loc = record.location
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (
                    record.share_id,
                    record.guardian_user_id,
                    record.protected_user_id,
                    record.reason,
                    record.shared_at,
                    loc.latitude,
                    loc.longitude,
                    loc.accuracy_meters,
                    loc.address,
                    loc.captured_at,
                ))
            finally:
                cursor.close()
