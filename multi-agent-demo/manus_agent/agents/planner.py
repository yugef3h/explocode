"""Planner sub-agent: decompose goal into subtasks."""

from __future__ import annotations

import json
import uuid
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from manus_agent.agents.base import BaseSubAgent
from manus_agent.config.settings import get_settings
from manus_agent.core.messages import PLANNER_SYSTEM, planner_user_prompt
from manus_agent.core.state import AgentState, SubTask
from manus_agent.llm.mock import extract_json_block


class PlannerAgent(BaseSubAgent):
    name = "planner"

    def run(self, state: AgentState) -> dict[str, Any]:
        settings = get_settings()
        goal = state.get("goal", "")
        system = PLANNER_SYSTEM.format(max_subtasks=settings.max_subtasks)
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=planner_user_prompt(goal)),
        ]
        response = self.llm.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)
        parsed = extract_json_block(raw) or json.loads(raw)
        subtasks: list[SubTask] = []
        for item in parsed[: settings.max_subtasks]:
            subtasks.append(
                {
                    "id": str(uuid.uuid4())[:8],
                    "title": item.get("title", "Task"),
                    "description": item.get("description", ""),
                    "status": "pending",
                }
            )
        self._remember(state, {"subtasks": subtasks})
        self.artifacts.write_json(state.get("run_id", "unknown"), "plan", subtasks)
        return {"subtasks": subtasks, "phase": "research"}
