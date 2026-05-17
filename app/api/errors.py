"""전역 예외 핸들러를 정의하여 일관된 에러 응답을 반환한다."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.security.jwt import JwtTokenError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """FastAPI 앱에 예외 핸들러들을 등록한다."""

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """잘못된 입력 값이나 비즈니스 로직 위반 시 400 에러를 반환한다."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError) -> JSONResponse:
        """권한이 없는 자원에 접근 시 403 에러를 반환한다."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(JwtTokenError)
    async def jwt_token_error_handler(request: Request, exc: JwtTokenError) -> JSONResponse:
        """유효하지 않거나 만료된 JWT 처리 시 401 에러를 반환한다."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """HTTPException은 그대로 반환한다."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """처리되지 않은 모든 예외에 대해 500 에러를 반환하고 로그를 남긴다."""
        logger.exception("Unhandled exception occurred: %s", str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error occurred."},
        )
