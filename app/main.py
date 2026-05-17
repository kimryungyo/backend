"""FastAPI 앱을 생성하고 v1 라우터와 DI context를 등록한다."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.v1.router import router as v1_router
from app.config.context import create_app_context
from app.database.mysql import MySQLPool


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """앱 시작/종료 시 MySQL connection pool 생명주기를 관리한다."""
    context = app.state.context
    mysql_pool = MySQLPool(context.settings)
    mysql_pool.initialize()
    context.mysql_pool = mysql_pool
    try:
        yield
    finally:
        mysql_pool.close()
        context.mysql_pool = None


def create_app() -> FastAPI:
    """재난안심 FastAPI 애플리케이션 인스턴스를 생성한다."""
    app = FastAPI(title="재난안심 API", lifespan=lifespan)
    app.state.context = create_app_context()

    # CORS 미들웨어를 추가한다.
    settings = app.state.context.settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 전역 예외 핸들러를 등록한다.
    register_exception_handlers(app)

    app.include_router(v1_router, prefix="/api/v1")

    @app.get("/health", tags=["Infrastructure"])
    async def health_check() -> dict[str, str]:
        """서버의 상태를 확인한다."""
        return {"status": "ok"}

    return app


app = create_app()
