"""Prompt templates for sub-agents."""

from __future__ import annotations

PLANNER_SYSTEM = """You are a planning agent. Break the user goal into concrete subtasks.
Return JSON array: [{"title": "...", "description": "..."}] max {max_subtasks} items."""

RESEARCHER_SYSTEM = """You are a research agent. For each subtask topic, summarize findings and list sources.
Be concise and factual."""

EXECUTOR_SYSTEM = """You are an execution agent. Complete subtasks and log concrete outcomes."""

WRITER_SYSTEM = """You are a technical writer. Produce a polished Markdown report from plan, research, and logs."""


def planner_user_prompt(goal: str) -> str:
    return f"Goal:\n{goal}\n\nProduce a task breakdown."


def researcher_user_prompt(goal: str, subtasks: list[dict]) -> str:
    lines = [f"Goal: {goal}", "Subtasks:"]
    for t in subtasks:
        lines.append(f"- {t.get('title')}: {t.get('description', '')}")
    return "\n".join(lines)


def writer_user_prompt(goal: str, plan: list[dict], research: list[dict], logs: list[str]) -> str:
    return (
        f"Goal: {goal}\n\nPlan: {plan}\n\nResearch: {research}\n\nExecution logs: {logs}\n\n"
        "Write the final report in Markdown."
    )
