# Manus-Style Multi-Agent Implementation Plan

> **For agentic workers:** Implement task-by-task with atomic commits after each file/function change.

**Goal:** Build a production-grade Python multi-agent system (main orchestrator + specialized sub-agents) that decomposes tasks, researches, stores memory, aggregates results, and outputs documents—similar to Manus.

**Architecture:** LangGraph state machine with a supervisor node routing to Planner → Researcher → Executor → Writer sub-agents. SQLite-backed episodic memory + file artifacts. Mock LLM mode for CI without API keys.

**Tech Stack:** Python 3.11+, LangGraph, LangChain Core, Pydantic v2, SQLite, pytest, optional OpenAI.

---

## Phase 1: Scaffold

- [x] Project layout under `multi-agent-demo/`
- [x] Auto-commit script
- [x] Core documentation (ARCHITECTURE, API, MEMORY, AGENTS)

## Phase 2: Core

- [ ] `manus_agent/config/settings.py` — env-based settings
- [ ] `manus_agent/core/state.py` — TypedDict graph state
- [ ] `manus_agent/core/messages.py` — message helpers
- [ ] `manus_agent/memory/store.py` — SQLite episodic store
- [ ] `manus_agent/memory/artifacts.py` — run artifact files

## Phase 3: Sub-Agents

- [ ] `manus_agent/agents/base.py` — BaseSubAgent protocol
- [ ] `manus_agent/agents/planner.py` — task decomposition
- [ ] `manus_agent/agents/researcher.py` — gather sources
- [ ] `manus_agent/agents/executor.py` — run subtasks
- [ ] `manus_agent/agents/writer.py` — final document

## Phase 4: Orchestration

- [ ] `manus_agent/llm/factory.py` — LLM + mock
- [ ] `manus_agent/core/graph.py` — LangGraph workflow
- [ ] `manus_agent/core/supervisor.py` — routing logic
- [ ] `manus_agent/cli.py` — CLI entry

## Phase 5: Quality

- [ ] Unit tests per module
- [ ] Integration test full pipeline (mock mode)
- [ ] README with quickstart
