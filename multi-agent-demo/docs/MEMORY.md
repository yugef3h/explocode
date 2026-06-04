# Memory Model

## Episodic Store (SQLite)

Table `memories`: each sub-agent append per step with `run_id`, `agent`, `phase`, JSON `payload`.

```python
from manus_agent.memory.store import MemoryStore
store = MemoryStore(Path(".manus_data/memory.db"))
store.append(run_id, "planner", "research", {"subtasks": [...]})
```

## Artifacts

Under `.manus_data/runs/<run_id>/`:

- `plan.json` — subtasks
- `research.json` — research items
- `execution.json` — logs
- `report.md` — final document

## Retention

Production deployments should TTL old runs (cron) or archive to object storage.
