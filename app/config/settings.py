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
    kakao_oauth_base_url: str = Field(default="https://kapi.kakao.com", description="카카오 API 기본 URL")
    push_provider_name: str = Field(default="stub", description="푸시 알림 제공자 이름")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
