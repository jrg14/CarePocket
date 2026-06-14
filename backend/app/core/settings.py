from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        enable_decoding=False,
    )

    app_name: str = "CarePocket API"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
    )

    database_url: str | None = None
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "carepocket"
    postgres_user: str = "carepocket"
    postgres_password: str = "carepocket"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: str | list[str] | None) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return ["http://localhost:3000"]
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @model_validator(mode="after")
    def _build_database_url(self) -> "Settings":
        if self.database_url:
            if self.database_url.startswith("postgresql://"):
                self.database_url = self.database_url.replace(
                    "postgresql://",
                    "postgresql+asyncpg://",
                    1,
                )
            elif self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace(
                    "postgres://",
                    "postgresql+asyncpg://",
                    1,
                )
            return self

        self.database_url = (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
