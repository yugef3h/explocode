"""LangGraph shared state definitions."""

from __future__ import annotations

import operator
from typing import Annotated, Literal, TypedDict


Phase = Literal["init", "plan", "research", "execute", "write", "done"]


class SubTask(TypedDict):
    id: str
    title: str
    description: str
    status: Literal["pending", "in_progress", "done", "failed"]


class ResearchItem(TypedDict):
    topic: str
    summary: str
    sources: list[str]


def merge_errors(left: list[str], right: list[str]) -> list[str]:
    return left + right


class AgentState(TypedDict, total=False):
    """State passed between graph nodes."""

    goal: str
    run_id: str
    phase: Phase
    subtasks: list[SubTask]
    research: Annotated[list[ResearchItem], operator.add]
    execution_log: Annotated[list[str], operator.add]
    errors: Annotated[list[str], merge_errors]
    document: str
    retry_count: int
