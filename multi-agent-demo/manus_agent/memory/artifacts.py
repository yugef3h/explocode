"""Filesystem artifacts per run (reports, intermediate JSON)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ArtifactStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def run_dir(self, run_id: str) -> Path:
        path = self.base_dir / "runs" / run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_json(self, run_id: str, name: str, data: Any) -> Path:
        path = self.run_dir(run_id) / f"{name}.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def write_text(self, run_id: str, name: str, content: str) -> Path:
        path = self.run_dir(run_id) / name
        path.write_text(content, encoding="utf-8")
        return path

    def read_text(self, run_id: str, name: str) -> str:
        return (self.run_dir(run_id) / name).read_text(encoding="utf-8")
