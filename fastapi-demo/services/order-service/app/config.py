from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    order_service_port: int = 8002
    user_service_url: str = "http://127.0.0.1:8001"


settings = Settings()
