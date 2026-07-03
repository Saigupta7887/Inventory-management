from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    database_url: str = "sqlite:///./inventory.db"
    upload_dir: str = "./uploads"

    anthropic_api_key: str = ""
    vision_model: str = "claude-opus-4-8"

    admin_email: str = "admin@example.com"
    admin_password: str = "admin1234"


@lru_cache
def get_settings() -> Settings:
    return Settings()
