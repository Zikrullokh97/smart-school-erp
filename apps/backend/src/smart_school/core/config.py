from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = Field(default="local")
    app_name: str = Field(default="Smart School Cloud ERP")
    app_public_url: str = Field(default="http://localhost:3000")
    api_public_url: str = Field(default="http://localhost:8000")
    database_url: str = Field(
        default="postgresql+asyncpg://smart_school:change-me-local@localhost:5432/smart_school"
    )
    jwt_issuer: str = Field(default="smart-school-cloud-erp")
    jwt_audience: str = Field(default="smart-school-users")
    jwt_access_token_minutes: int = Field(default=15, ge=1, le=120)
    jwt_refresh_token_days: int = Field(default=30, ge=1, le=90)
    jwt_private_key_path: Path = Field(default=Path("secrets/jwt_private.pem"))
    jwt_public_key_path: Path = Field(default=Path("secrets/jwt_public.pem"))
    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(64), min_length=32)

    @property
    def alembic_database_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")


@lru_cache
def get_settings() -> Settings:
    return Settings()
