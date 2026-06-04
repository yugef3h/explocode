# Sub-Agents

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Planner** | Decompose goal | `goal` | `subtasks[]`, phase→research |
| **Researcher** | Gather knowledge | `subtasks` | `research[]`, phase→execute |
| **Executor** | Complete work items | `subtasks` | `execution_log[]`, updated statuses |
| **Writer** | Final deliverable | plan + research + logs | `document` (Markdown) |

## Supervisor

The graph entry is **Planner**; linear edges Planner → Researcher → Executor → Writer → END. `supervisor.next_node` supports future conditional routing on errors.

## Extension

Add a node in `core/graph.py` and implement `BaseSubAgent.run()`.
