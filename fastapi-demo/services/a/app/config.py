from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# fastapi-demo/services/a/app/config.py -> fastapi-demo/.env
_BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_BASE_DIR / ".env", extra="ignore")

    a_service_port: int = 8003
    redis_om_url: str = "redis://localhost:6379"


settings = Settings()
