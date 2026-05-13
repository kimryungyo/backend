"""JWT access/refresh token 발급과 검증 유틸리티를 정의한다."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Protocol

from jose import ExpiredSignatureError, JWTError, jwt

from app.domain.enums import UserRole

TokenType = Literal["access", "refresh"]

_SUBJECT_CLAIM = "sub"
_TOKEN_TYPE_CLAIM = "token_type"
_ROLE_CLAIM = "role"
_ISSUED_AT_CLAIM = "iat"
_EXPIRES_AT_CLAIM = "exp"
_RESERVED_CLAIMS = {
    _SUBJECT_CLAIM,
    _TOKEN_TYPE_CLAIM,
    _ROLE_CLAIM,
    _ISSUED_AT_CLAIM,
    _EXPIRES_AT_CLAIM,
}


class JwtSettings(Protocol):
    """JWT 유틸리티가 참조하는 Settings 필드 계약."""

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int


class JwtTokenError(ValueError):
    """JWT 처리 중 발생하는 기본 예외."""


class JwtSecretNotConfiguredError(JwtTokenError):
    """JWT secret key가 설정되지 않았을 때 발생하는 예외."""


class JwtTokenExpiredError(JwtTokenError):
    """JWT가 만료되었을 때 발생하는 예외."""


class JwtTokenInvalidError(JwtTokenError):
    """JWT 형식, 서명, 필수 claim이 유효하지 않을 때 발생하는 예외."""


@dataclass(frozen=True)
class JwtTokenClaims:
    """검증된 JWT claim 정보를 나타낸다."""

    user_id: str
    token_type: TokenType
    issued_at: datetime
    expires_at: datetime
    role: UserRole | None = None


class JwtTokenManager:
    """Settings 기반 JWT access/refresh token 발급과 검증을 담당한다."""

    def __init__(self, settings: JwtSettings) -> None:
        self._settings = settings

    def create_access_token(
        self,
        user_id: str,
        role: UserRole | None = None,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """사용자 식별자를 subject로 하는 access token을 발급한다."""
        expires_delta = timedelta(minutes=self._settings.jwt_access_token_expire_minutes)
        return self._create_token(user_id, "access", expires_delta, role, extra_claims)

    def create_refresh_token(
        self,
        user_id: str,
        role: UserRole | None = None,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """사용자 식별자를 subject로 하는 refresh token을 발급한다."""
        expires_delta = timedelta(days=self._settings.jwt_refresh_token_expire_days)
        return self._create_token(user_id, "refresh", expires_delta, role, extra_claims)

    def verify_access_token(self, token: str) -> JwtTokenClaims:
        """access token을 검증하고 claim 정보를 반환한다."""
        return self.verify_token(token, expected_token_type="access")

    def verify_refresh_token(self, token: str) -> JwtTokenClaims:
        """refresh token을 검증하고 claim 정보를 반환한다."""
        return self.verify_token(token, expected_token_type="refresh")

    def verify_token(self, token: str, expected_token_type: TokenType | None = None) -> JwtTokenClaims:
        """JWT 서명, 만료 시간, 필수 claim, token type을 검증한다."""
        secret_key = self._require_secret_key()
        try:
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[self._settings.jwt_algorithm],
            )
        except ExpiredSignatureError as exc:
            raise JwtTokenExpiredError("JWT token has expired") from exc
        except JWTError as exc:
            raise JwtTokenInvalidError("JWT token is invalid") from exc

        return self._parse_claims(payload, expected_token_type)

    def _create_token(
        self,
        user_id: str,
        token_type: TokenType,
        expires_delta: timedelta,
        role: UserRole | None,
        extra_claims: dict[str, Any] | None,
    ) -> str:
        secret_key = self._require_secret_key()
        now = datetime.now(timezone.utc)
        expires_at = now + expires_delta

        payload = self._validated_extra_claims(extra_claims)
        payload.update(
            {
                _SUBJECT_CLAIM: user_id,
                _TOKEN_TYPE_CLAIM: token_type,
                _ISSUED_AT_CLAIM: now,
                _EXPIRES_AT_CLAIM: expires_at,
            }
        )
        if role is not None:
            payload[_ROLE_CLAIM] = role.value

        return jwt.encode(payload, secret_key, algorithm=self._settings.jwt_algorithm)

    def _require_secret_key(self) -> str:
        secret_key = self._settings.jwt_secret_key.strip()
        if not secret_key:
            raise JwtSecretNotConfiguredError("JWT_SECRET_KEY is not configured")
        return secret_key

    def _validated_extra_claims(self, extra_claims: dict[str, Any] | None) -> dict[str, Any]:
        if not extra_claims:
            return {}

        reserved_claims = _RESERVED_CLAIMS.intersection(extra_claims)
        if reserved_claims:
            claims = ", ".join(sorted(reserved_claims))
            raise JwtTokenInvalidError(f"extra_claims cannot override reserved claims: {claims}")
        return dict(extra_claims)

    def _parse_claims(
        self,
        payload: dict[str, Any],
        expected_token_type: TokenType | None,
    ) -> JwtTokenClaims:
        user_id = payload.get(_SUBJECT_CLAIM)
        token_type = payload.get(_TOKEN_TYPE_CLAIM)
        issued_at = payload.get(_ISSUED_AT_CLAIM)
        expires_at = payload.get(_EXPIRES_AT_CLAIM)

        if not isinstance(user_id, str) or not user_id:
            raise JwtTokenInvalidError("JWT subject claim is missing")
        if token_type not in {"access", "refresh"}:
            raise JwtTokenInvalidError("JWT token_type claim is invalid")
        if expected_token_type is not None and token_type != expected_token_type:
            raise JwtTokenInvalidError("JWT token_type claim does not match expected type")

        role = self._parse_role(payload.get(_ROLE_CLAIM))
        return JwtTokenClaims(
            user_id=user_id,
            token_type=token_type,
            role=role,
            issued_at=self._parse_timestamp(issued_at, _ISSUED_AT_CLAIM),
            expires_at=self._parse_timestamp(expires_at, _EXPIRES_AT_CLAIM),
        )

    def _parse_role(self, role: Any) -> UserRole | None:
        if role is None:
            return None
        try:
            return UserRole(role)
        except ValueError as exc:
            raise JwtTokenInvalidError("JWT role claim is invalid") from exc

    def _parse_timestamp(self, value: Any, claim_name: str) -> datetime:
        if not isinstance(value, int):
            raise JwtTokenInvalidError(f"JWT {claim_name} claim is invalid")
        return datetime.fromtimestamp(value, tz=timezone.utc)
