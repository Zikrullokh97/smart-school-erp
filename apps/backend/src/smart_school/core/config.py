from __future__ import annotations

from functools import lru_cache

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
    database_url: str = Field(
        default="postgresql+asyncpg://smart_school:change-me-local@localhost:5432/smart_school"
    )

    @property
    def alembic_database_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")


@lru_cache
def get_settings() -> Settings:
    return Settings()
