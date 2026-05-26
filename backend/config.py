from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = parent of backend/. Lets the app find .env regardless of CWD.
ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT_DIR / ".env"), extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://riego_user:riego_pass_change_me@postgres:5432/riego_db"
    SECRET_KEY: str = "change-me"
    ENVIRONMENT: str = "development"
    SEED_ON_STARTUP: bool = True
    SITE_NAME: str = "Aqua-Terra"
    SITE_TAGLINE: str = "Soluciones Integrales en Agua y Tierra"
    CONTACT_EMAIL: str = "contacto@aquaterra.com"
    CONTACT_PHONE: str = "+51 1 234 5678"
    # Default admin (created on first boot if no admin exists)
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@aquaterra.com"
    ADMIN_PASSWORD: str = "AquaTerra2026!"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
