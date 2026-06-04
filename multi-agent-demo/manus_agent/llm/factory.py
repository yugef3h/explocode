"""LLM factory: OpenAI or mock."""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from manus_agent.config.settings import Settings, get_settings
from manus_agent.llm.mock import MockChatModel


def get_chat_model(settings: Settings | None = None) -> BaseChatModel:
    cfg = settings or get_settings()
    provider = cfg.llm_provider.lower()
    if provider == "mock":
        return MockChatModel()
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        if cfg.openai_api_key:
            return ChatOpenAI(
                model=cfg.openai_model,
                api_key=cfg.openai_api_key,  # type: ignore[arg-type]
            )
        return ChatOpenAI(model=cfg.openai_model)
    raise ValueError(f"Unknown llm_provider: {cfg.llm_provider}")
