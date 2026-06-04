"""LangGraph workflow assembly."""

from __future__ import annotations

import uuid
from typing import Any, cast

from langgraph.graph import END, StateGraph

from manus_agent.agents.executor import ExecutorAgent
from manus_agent.agents.planner import PlannerAgent
from manus_agent.agents.researcher import ResearcherAgent
from manus_agent.agents.writer import WriterAgent
from manus_agent.config.settings import Settings, get_settings
from manus_agent.core.state import AgentState
from manus_agent.core.supervisor import next_node
from manus_agent.llm.factory import get_chat_model
from manus_agent.memory.artifacts import ArtifactStore
from manus_agent.memory.store import MemoryStore


def _wrap(agent_method):
    def node(state: AgentState) -> dict[str, Any]:
        return agent_method(state)

    return node


def build_graph(settings: Settings | None = None):
    cfg = settings or get_settings()
    llm = get_chat_model(cfg)
    memory = MemoryStore(cfg.data_dir / "memory.db")
    artifacts = ArtifactStore(cfg.data_dir)

    planner = PlannerAgent(llm, memory, artifacts)
    researcher = ResearcherAgent(llm, memory, artifacts)
    executor = ExecutorAgent(llm, memory, artifacts)
    writer = WriterAgent(llm, memory, artifacts)

    graph = StateGraph(AgentState)

    graph.add_node("planner", _wrap(planner.run))
    graph.add_node("researcher", _wrap(researcher.run))
    graph.add_node("executor", _wrap(executor.run))
    graph.add_node("writer", _wrap(writer.run))

    graph.set_entry_point("planner")

    def route_after_planner(state: AgentState) -> str:
        return "researcher"

    def route_after_researcher(state: AgentState) -> str:
        return "executor"

    def route_after_executor(state: AgentState) -> str:
        return "writer"

    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "executor")
    graph.add_edge("executor", "writer")
    graph.add_edge("writer", END)

    return graph.compile()


def run_workflow(goal: str, settings: Settings | None = None) -> AgentState:
    cfg = settings or get_settings()
    run_id = str(uuid.uuid4())
    app = build_graph(cfg)
    initial: AgentState = {
        "goal": goal,
        "run_id": run_id,
        "phase": "init",
        "subtasks": [],
        "research": [],
        "execution_log": [],
        "errors": [],
        "retry_count": 0,
        "document": "",
    }
    final = app.invoke(initial)
    artifacts = ArtifactStore(cfg.data_dir)
    if final.get("document"):
        artifacts.write_text(run_id, "report.md", final["document"])
    return cast(AgentState, final)
