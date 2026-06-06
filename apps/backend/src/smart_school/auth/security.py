from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher, exceptions

from smart_school.core.config import get_settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

pwd_context = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=4)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(password_hash, plain_password)
    except (exceptions.VerifyMismatchError, exceptions.VerificationError):
        return False


def hash_refresh_token(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()


def _load_jwt_keys() -> tuple[str, str, str]:
    settings = get_settings()
    if settings.jwt_private_key_path.exists() and settings.jwt_public_key_path.exists():
        private_key = settings.jwt_private_key_path.read_text()
        public_key = settings.jwt_public_key_path.read_text()
        return "RS256", private_key, public_key

    secret = settings.jwt_secret_key
    return "HS256", secret, secret


def create_access_token(user_id: str, tenant_id: str) -> tuple[str, int]:
    algorithm, private_key, _public_key = _load_jwt_keys()
    settings = get_settings()
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.jwt_access_token_minutes)
    payload: dict[str, Any] = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "type": ACCESS_TOKEN_TYPE,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    token = jwt.encode(payload, private_key, algorithm=algorithm)
    return token, int((expires_at - now).total_seconds())


def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def decode_jwt_token(token: str, expected_type: str) -> dict[str, Any]:
    algorithm, _private_key, public_key = _load_jwt_keys()
    settings = get_settings()
    payload = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Invalid token type")
    return payload
