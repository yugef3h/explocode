from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_BASE_DIR / ".env", extra="ignore")

    user_service_port: int = 8001
    grpc_port: int = 50051


settings = Settings()
