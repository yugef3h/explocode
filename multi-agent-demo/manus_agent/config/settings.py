"""Application settings loaded from environment."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MANUS_", env_file=".env", extra="ignore")

    llm_provider: str = Field(default="mock", description="mock | openai")
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")
    data_dir: Path = Field(default=Path(".manus_data"))
    max_subtasks: int = Field(default=8, ge=1, le=32)
    max_research_rounds: int = Field(default=2, ge=1, le=5)
    max_retries: int = Field(default=2, ge=0, le=5)


@lru_cache
def get_settings() -> Settings:
    return Settings()
