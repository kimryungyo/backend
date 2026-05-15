"""환경변수와 서버 설정 값을 관리한다."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """FastAPI 서버와 외부 연동에 필요한 설정 값을 보관한다."""

    app_env: str = Field(default="local", description="애플리케이션 실행 환경")
    app_name: str = Field(default="재난안심 API", description="FastAPI 앱 이름")
    disaster_catalog_path: Path = Field(
        default=Path("app/data/disaster_catalog.example.json"),
        description="재난 카탈로그 JSON 파일 경로",
    )

    mysql_host: str = Field(default="localhost", description="MySQL 서버 호스트")
    mysql_port: int = Field(default=3306, description="MySQL 서버 포트")
    mysql_user: str = Field(default="safe_app", description="MySQL 사용자 이름")
    mysql_password: str = Field(default="", description="MySQL 사용자 비밀번호")
    mysql_database: str = Field(default="safe_app", description="MySQL 데이터베이스 이름")
    mysql_charset: str = Field(default="utf8mb4", description="MySQL 문자셋")
    mysql_pool_name: str = Field(default="safe_app_pool", description="MySQL connection pool 이름")
    mysql_pool_size: int = Field(default=5, ge=1, le=32, description="MySQL connection pool 크기")
    mysql_autocommit: bool = Field(default=False, description="MySQL connection autocommit 사용 여부")
    mysql_connection_timeout_seconds: int = Field(default=10, ge=1, description="MySQL 연결 timeout(초)")

    oauth_client_id: str = Field(default="", description="OAuth 클라이언트 ID")
    oauth_client_secret: str = Field(default="", description="OAuth 클라이언트 secret")
    oauth_redirect_uri: str = Field(default="", description="OAuth redirect URI")
    kakao_oauth_base_url: str = Field(default="https://kapi.kakao.com", description="카카오 API 기본 URL")

    jwt_secret_key: str = Field(default="", description="JWT 서명 secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT 서명 알고리즘")
    jwt_access_token_expire_minutes: int = Field(default=60, description="JWT access token 만료 시간(분)")
    jwt_refresh_token_expire_days: int = Field(default=14, description="JWT refresh token 만료 시간(일)")

    push_provider_name: str = Field(default="stub", description="푸시 알림 제공자 이름")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
