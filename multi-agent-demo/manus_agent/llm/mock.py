"""Deterministic mock LLM for offline runs and tests."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class MockChatModel(BaseChatModel):
    """Rule-based responses keyed off prompt keywords."""

    @property
    def _llm_type(self) -> str:
        return "mock-manus"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        text = "\n".join(getattr(m, "content", "") or "" for m in messages)
        reply = self._route(text)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=reply))])

    def _route(self, prompt: str) -> str:
        lower = prompt.lower()
        if "task breakdown" in lower or "planning agent" in lower:
            return json.dumps(
                [
                    {"title": "Scope", "description": "Define scope and constraints"},
                    {"title": "Research", "description": "Gather references and patterns"},
                    {"title": "Synthesize", "description": "Merge findings into report"},
                ]
            )
        if "research agent" in lower:
            return json.dumps(
                {
                    "topic": "multi-agent orchestration",
                    "summary": "LangGraph provides stateful graphs; supervisors route sub-agents.",
                    "sources": ["langchain docs", "manus architecture patterns"],
                }
            )
        if "execution agent" in lower:
            return "Executed subtasks: scoped goal, validated research notes, prepared writer input."
        if "technical writer" in lower:
            return (
                "# Multi-Agent Report\n\n"
                "## Summary\n"
                "Mock run completed successfully.\n\n"
                "## Plan\n"
                "Scope → Research → Synthesize\n\n"
                "## Findings\n"
                "Supervisor orchestration with episodic memory is production-viable.\n"
            )
        return "Acknowledged."

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {"model": "mock-manus"}


def extract_json_block(text: str) -> Any:
    match = re.search(r"\[.*\]|\{.*\}", text, re.DOTALL)
    if not match:
        return None
    return json.loads(match.group())
