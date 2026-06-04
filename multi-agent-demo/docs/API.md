# Python API

## Run workflow

```python
from manus_agent.core.graph import run_workflow
from manus_agent.config.settings import Settings

result = run_workflow(
    "Write a report on multi-agent memory",
    Settings(llm_provider="mock"),
)
print(result["document"])
```

## Build graph only

```python
from manus_agent.core.graph import build_graph

app = build_graph()
state = app.invoke({"goal": "...", "run_id": "x", "phase": "init"})
```

## Memory inspection

```python
from pathlib import Path
from manus_agent.memory.store import MemoryStore

records = MemoryStore(Path(".manus_data/memory.db")).list_run(run_id)
```
