from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core
    app_name: str = "Bondly API"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql+psycopg2://bondly:bondly@localhost:5432/bondly"

    # Auth
    secret_key: str = "change-me-in-production-please-use-a-long-random-string"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    algorithm: str = "HS256"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Social login (leave blank to disable that provider).
    # Google OAuth client ID (the web client ID from Google Cloud Console).
    google_client_id: str = ""
    # Apple "Services ID" / client ID configured in the Apple Developer portal.
    # Comma-separated to allow both a web Services ID and a native bundle ID.
    apple_client_ids: str = ""

    @property
    def apple_client_id_list(self) -> list[str]:
        return [a.strip() for a in self.apple_client_ids.split(",") if a.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
