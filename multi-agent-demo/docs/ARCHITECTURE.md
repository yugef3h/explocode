# Architecture

## Overview

The system mimics a **Manus-style** autonomous agent: one **supervisor** coordinates specialized **sub-agents** over a shared **LangGraph** state machine. Each run produces structured artifacts and a final Markdown document.

```
User Goal
    │
    ▼
┌─────────────┐
│  Supervisor │── routes by phase / errors
└──────┬──────┘
       │
   ┌───┴───┬──────────┬──────────┐
   ▼       ▼          ▼          ▼
Planner Researcher Executor  Writer
   │       │          │          │
   └───┬───┴────┬─────┴────┬─────┘
       ▼        ▼          ▼
   SQLite Memory + Artifact Store
       │
       ▼
  output/report.md
```

## Layers

| Layer | Responsibility |
|-------|----------------|
| **CLI** | `manus run`, config flags |
| **Graph** | LangGraph nodes & edges |
| **Supervisor** | Next-agent routing |
| **Sub-agents** | Domain logic per role |
| **Memory** | Episodic SQLite + JSON artifacts |
| **LLM** | OpenAI or deterministic mock |

## State Machine

Phases: `init → plan → research → execute → write → done`.

The supervisor reads `AgentState.phase` and optional retry counters. Failed subtasks bump `errors` and may re-route to research or planner.

## Design Principles

1. **Small nodes** — each sub-agent is a pure function `state → partial state`.
2. **Inspectable memory** — every step appends to SQLite for replay.
3. **Offline-first** — mock LLM enables CI without network.
4. **Atomic dev commits** — one commit per file/function change during development.
