from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite+aiosqlite:///./agent.db"
    redis_url: str = "redis://localhost:6379/0"
    xai_api_key: str | None = None
    xai_fast_model: str = "grok-4.1-fast"
    xai_balanced_model: str = "grok-4.1-fast"
    xai_strong_model: str = "grok-4.6"
    cors_origins_raw: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins_raw.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
