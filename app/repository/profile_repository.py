"""보호자와 보호대상자 프로필 저장소 인터페이스를 정의한다."""

from abc import ABC, abstractmethod

from app.database.mysql import MySQLPool
from app.domain.enums import ProtectedCategory
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

    @abstractmethod
    def save_guardian_profile(self, profile: GuardianProfile) -> None:
        """보호자 프로필을 저장한다."""
        raise NotImplementedError


class MySQLProfileRepository(ProfileRepository):
    """MySQL 기반 프로필 repository 구현체."""

    def __init__(self, mysql_pool: MySQLPool) -> None:
        self._pool = mysql_pool

    def get_protected_profile(self, user_id: str) -> ProtectedProfile:
        """보호대상자 프로필을 조회한다."""
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT user_id, region_code, auto_location_share_enabled, updated_at"
                " FROM protected_profiles WHERE user_id = %s",
                (user_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise KeyError(user_id)

            cursor.execute(
                "SELECT category FROM protected_profile_categories WHERE user_id = %s",
                (user_id,),
            )
            categories = [ProtectedCategory(r["category"]) for r in cursor.fetchall()]

        return ProtectedProfile(
            user_id=row["user_id"],
            categories=categories,
            region_code=row["region_code"],
            auto_location_share_enabled=bool(row["auto_location_share_enabled"]),
            updated_at=row["updated_at"],
        )

    def save_protected_profile(self, profile: ProtectedProfile) -> None:
        """보호대상자 프로필을 저장한다."""
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO protected_profiles
                        (user_id, region_code, auto_location_share_enabled, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        region_code = VALUES(region_code),
                        auto_location_share_enabled = VALUES(auto_location_share_enabled),
                        updated_at = VALUES(updated_at)
                    """,
                    (
                        profile.user_id,
                        profile.region_code,
                        int(profile.auto_location_share_enabled),
                        profile.updated_at,
                    ),
                )
                cursor.execute(
                    "DELETE FROM protected_profile_categories WHERE user_id = %s",
                    (profile.user_id,),
                )
                if profile.categories:
                    cursor.executemany(
                        "INSERT INTO protected_profile_categories (user_id, category) VALUES (%s, %s)",
                        [(profile.user_id, cat.value) for cat in profile.categories],
                    )
            finally:
                cursor.close()

    def get_guardian_profile(self, user_id: str) -> GuardianProfile:
        """보호자 프로필을 조회한다."""
        with self._pool.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT user_id, phone_number, updated_at FROM guardian_profiles WHERE user_id = %s",
                (user_id,),
            )
            row = cursor.fetchone()
        if row is None:
            raise KeyError(user_id)
        return GuardianProfile(
            user_id=row["user_id"],
            phone_number=row["phone_number"],
            updated_at=row["updated_at"],
        )

    def save_guardian_profile(self, profile: GuardianProfile) -> None:
        """보호자 프로필을 저장한다."""
        sql = """
            INSERT INTO guardian_profiles (user_id, phone_number, updated_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                phone_number = VALUES(phone_number),
                updated_at = VALUES(updated_at)
        """
        with self._pool.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (profile.user_id, profile.phone_number, profile.updated_at))
            finally:
                cursor.close()
