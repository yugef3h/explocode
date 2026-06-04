"""Writer sub-agent: produce final Markdown document."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from manus_agent.agents.base import BaseSubAgent
from manus_agent.core.messages import WRITER_SYSTEM, writer_user_prompt
from manus_agent.core.state import AgentState


class WriterAgent(BaseSubAgent):
    name = "writer"

    def run(self, state: AgentState) -> dict[str, Any]:
        goal = state.get("goal", "")
        subtasks = state.get("subtasks", [])
        research = state.get("research", [])
        logs = state.get("execution_log", [])
        messages = [
            SystemMessage(content=WRITER_SYSTEM),
            HumanMessage(
                content=writer_user_prompt(goal, subtasks, research, logs)
            ),
        ]
        response = self.llm.invoke(messages)
        document = (
            response.content if isinstance(response.content, str) else str(response.content)
        )
        run_id = state.get("run_id", "unknown")
        self._remember(state, {"document_len": len(document)})
        self.artifacts.write_text(run_id, "report.md", document)
        return {"document": document, "phase": "done"}
