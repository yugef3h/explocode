"""Supervisor routing: decide next graph node from phase."""

from __future__ import annotations

from manus_agent.core.state import AgentState, Phase


def next_node(state: AgentState) -> str:
    """Return LangGraph node name for current phase."""
    phase: Phase = state.get("phase", "init")  # type: ignore[assignment]
    errors = state.get("errors", [])
    retry = state.get("retry_count", 0)

    if phase == "done":
        return "end"
    if phase == "init":
        return "planner"
    if phase == "plan":
        return "planner"
    if phase == "research":
        return "researcher"
    if phase == "execute":
        return "executor"
    if phase == "write":
        return "writer"
    if errors and retry < 2:
        return "researcher"
    return "writer"
