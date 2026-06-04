"""Researcher sub-agent: gather notes per subtask."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from manus_agent.agents.base import BaseSubAgent
from manus_agent.core.messages import RESEARCHER_SYSTEM, researcher_user_prompt
from manus_agent.core.state import AgentState, ResearchItem
from manus_agent.llm.mock import extract_json_block
from manus_agent.tools.search import search


class ResearcherAgent(BaseSubAgent):
    name = "researcher"

    def run(self, state: AgentState) -> dict[str, Any]:
        goal = state.get("goal", "")
        subtasks = state.get("subtasks", [])
        items: list[ResearchItem] = []
        for task in subtasks:
            messages = [
                SystemMessage(content=RESEARCHER_SYSTEM),
                HumanMessage(
                    content=researcher_user_prompt(
                        f"{goal} — {task.get('title')}", [task]
                    )
                ),
            ]
            response = self.llm.invoke(messages)
            raw = response.content if isinstance(response.content, str) else str(response.content)
            parsed = extract_json_block(raw)
            local_sources = [h["url"] for h in search(task.get("title", goal))]
            if isinstance(parsed, dict):
                merged = list(parsed.get("sources", [])) + local_sources
                items.append(
                    {
                        "topic": parsed.get("topic", task.get("title", "")),
                        "summary": parsed.get("summary", raw[:500]),
                        "sources": merged,
                    }
                )
            else:
                items.append(
                    {
                        "topic": task.get("title", ""),
                        "summary": raw[:500],
                        "sources": [],
                    }
                )
        self._remember(state, {"research": items})
        self.artifacts.write_json(state.get("run_id", "unknown"), "research", items)
        return {"research": items, "phase": "execute"}
