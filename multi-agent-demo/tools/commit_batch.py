#!/usr/bin/env python3
"""Write files and create one git commit per entry."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def commit(message: str, rel_path: str, content: str) -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", rel_path], cwd=ROOT, check=True)
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if r.returncode == 0:
        return
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    print(f"ok: {message}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: commit_batch.py <batch.py>")
        raise SystemExit(1)
    ns: dict = {}
    exec(Path(sys.argv[1]).read_text(), ns)  # noqa: S102
    for message, rel_path, content in ns["COMMITS"]:
        commit(message, rel_path, content)


if __name__ == "__main__":
    main()
