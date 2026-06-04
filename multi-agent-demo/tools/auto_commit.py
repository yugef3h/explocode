#!/usr/bin/env python3
"""Atomic git commit helper for multi-agent-demo development."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / ".git").exists():
            return parent
    raise SystemExit("No git repository found")


def run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr or result.stdout)
        raise SystemExit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage paths and commit atomically")
    parser.add_argument("message", help="Commit message")
    parser.add_argument("paths", nargs="*", help="Paths to stage (default: all)")
    args = parser.parse_args()

    root = repo_root()
    paths = args.paths or ["."]
    run(["git", "add", *paths], root)
    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=root,
    )
    if status.returncode == 0:
        print("Nothing to commit")
        return
    run(["git", "commit", "-m", args.message], root)
    print(f"Committed: {args.message}")


if __name__ == "__main__":
    main()
