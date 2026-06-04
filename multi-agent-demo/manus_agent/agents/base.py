"""Base class for sub-agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from manus_agent.core.state import AgentState
from manus_agent.memory.artifacts import ArtifactStore
from manus_agent.memory.store import MemoryStore


class BaseSubAgent(ABC):
    name: str = "base"

    def __init__(
        self,
        llm: BaseChatModel,
        memory: MemoryStore,
        artifacts: ArtifactStore,
    ) -> None:
        self.llm = llm
        self.memory = memory
        self.artifacts = artifacts

    @abstractmethod
    def run(self, state: AgentState) -> dict[str, Any]:
        """Return partial state update."""

    def _remember(self, state: AgentState, payload: dict[str, Any]) -> None:
        run_id = state.get("run_id", "unknown")
        phase = state.get("phase", "unknown")
        self.memory.append(run_id, self.name, str(phase), payload)
