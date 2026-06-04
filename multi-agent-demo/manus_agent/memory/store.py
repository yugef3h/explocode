"""SQLite episodic memory for agent runs."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class MemoryRecord:
    id: int
    run_id: str
    agent: str
    phase: str
    payload: dict[str, Any]
    created_at: str


class MemoryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_run ON memories(run_id)"
            )

    def append(self, run_id: str, agent: str, phase: str, payload: dict[str, Any]) -> int:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO memories (run_id, agent, phase, payload, created_at) VALUES (?,?,?,?,?)",
                (run_id, agent, phase, json.dumps(payload), now),
            )
            return int(cur.lastrowid)

    def list_run(self, run_id: str) -> list[MemoryRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM memories WHERE run_id = ? ORDER BY id",
                (run_id,),
            ).fetchall()
        return [
            MemoryRecord(
                id=r["id"],
                run_id=r["run_id"],
                agent=r["agent"],
                phase=r["phase"],
                payload=json.loads(r["payload"]),
                created_at=r["created_at"],
            )
            for r in rows
        ]
