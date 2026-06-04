from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_BASE_DIR / ".env", extra="ignore")

    order_service_port: int = 8002
    user_service_grpc_target: str = "127.0.0.1:50051"
    a_service_grpc_target: str = "127.0.0.1:50053"
    redis_om_url: str = "redis://localhost:6379"


settings = Settings()
