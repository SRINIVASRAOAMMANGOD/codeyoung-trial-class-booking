"""
config.py — Application settings loaded from environment variables.

pydantic-settings reads values from the .env file automatically.
Accessing settings via get_settings() (with @lru_cache) ensures the
.env file is parsed only once per process.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    app_env: str = "development"

    # Email notification settings
    email_backend: str = "console"  # "console" for dev simulation, "smtp" for real delivery
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-reply@codeyoung.com"
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
