"""Executor sub-agent: run subtasks and append logs."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from manus_agent.agents.base import BaseSubAgent
from manus_agent.core.messages import EXECUTOR_SYSTEM
from manus_agent.core.state import AgentState


class ExecutorAgent(BaseSubAgent):
    name = "executor"

    def run(self, state: AgentState) -> dict[str, Any]:
        subtasks = list(state.get("subtasks", []))
        logs: list[str] = []
        for i, task in enumerate(subtasks):
            subtasks[i] = {**task, "status": "in_progress"}
            messages = [
                SystemMessage(content=EXECUTOR_SYSTEM),
                HumanMessage(
                    content=f"Execute: {task.get('title')} — {task.get('description', '')}"
                ),
            ]
            response = self.llm.invoke(messages)
            text = response.content if isinstance(response.content, str) else str(response.content)
            logs.append(f"[{task.get('id')}] {task.get('title')}: {text.strip()[:300]}")
            subtasks[i] = {**subtasks[i], "status": "done"}
        self._remember(state, {"execution_log": logs, "subtasks": subtasks})
        self.artifacts.write_json(state.get("run_id", "unknown"), "execution", logs)
        return {"subtasks": subtasks, "execution_log": logs, "phase": "write"}
