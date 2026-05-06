"""FastAPI 앱을 생성하고 v1 라우터와 DI context를 등록한다."""

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.config.context import create_app_context


def create_app() -> FastAPI:
    """재난안심 FastAPI 애플리케이션 인스턴스를 생성한다."""
    app = FastAPI(title="재난안심 API")
    app.state.context = create_app_context()
    app.include_router(v1_router, prefix="/api/v1")
    return app


app = create_app()
