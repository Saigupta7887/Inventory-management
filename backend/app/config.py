from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Runtime ---
    environment: str = "development"  # development | production
    debug: bool = True
    log_level: str = "INFO"

    # --- Security ---
    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week
    media_token_expire_minutes: int = 60  # short-lived, used only for image URLs
    # Comma-separated list, or "*" for all (dev only).
    allowed_origins: str = "*"

    # --- Database ---
    database_url: str = "sqlite:///./inventory.db"
    # In dev we create tables on boot; in prod use Alembic migrations instead.
    auto_create_tables: bool = True

    # --- Storage ---
    storage_backend: str = "local"  # local | s3
    upload_dir: str = "./uploads"
    s3_bucket: str = ""
    s3_region: str = ""
    s3_endpoint_url: str = ""  # optional, for S3-compatible providers

    # --- AI ---
    anthropic_api_key: str = ""
    vision_model: str = "claude-opus-4-8"

    # --- Seed admin ---
    admin_email: str = "admin@example.com"
    admin_password: str = "admin1234"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def cors_origins(self) -> list[str]:
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @field_validator("environment")
    @classmethod
    def _normalize_env(cls, v: str) -> str:
        return v.lower()

    def validate_for_production(self) -> None:
        """Fail fast on unsafe production configuration."""
        if not self.is_production:
            return
        problems = []
        if self.secret_key == "dev-secret-change-me" or len(self.secret_key) < 32:
            problems.append("SECRET_KEY must be set to a strong value (>=32 chars) in production")
        if "*" in self.cors_origins:
            problems.append("ALLOWED_ORIGINS must be an explicit list in production, not '*'")
        if self.admin_password == "admin1234":
            problems.append("ADMIN_PASSWORD must be changed in production")
        if self.storage_backend == "s3" and not self.s3_bucket:
            problems.append("S3_BUCKET is required when STORAGE_BACKEND=s3")
        if problems:
            raise RuntimeError("Insecure production configuration:\n  - " + "\n  - ".join(problems))


@lru_cache
def get_settings() -> Settings:
    return Settings()
