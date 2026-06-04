from pathlib import Path

from manus_agent.memory.store import MemoryStore


def test_append_and_list(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "m.db")
    mid = store.append("run-1", "planner", "plan", {"k": 1})
    assert mid == 1
    rows = store.list_run("run-1")
    assert len(rows) == 1
    assert rows[0].agent == "planner"
    assert rows[0].payload["k"] == 1
