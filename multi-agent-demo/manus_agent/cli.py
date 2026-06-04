"""CLI entry: manus run <goal>."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from manus_agent.config.settings import Settings
from manus_agent.core.graph import run_workflow

app = typer.Typer(help="Manus-style multi-agent CLI")
console = Console()


@app.command("run")
def run_cmd(
    goal: str = typer.Argument(..., help="User goal / task description"),
    llm: str = typer.Option("mock", "--llm", help="mock | openai"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Save report path"),
    data_dir: Path | None = typer.Option(None, "--data-dir", help="Runtime data directory"),
) -> None:
    settings = Settings(llm_provider=llm)
    if data_dir:
        settings = Settings(llm_provider=llm, data_dir=data_dir)
    console.print(Panel(f"[bold]Goal[/bold]\n{goal}", title="Manus Agent"))
    result = run_workflow(goal, settings)
    doc = result.get("document", "")
    run_id = result.get("run_id", "")
    console.print(f"[green]Run complete[/green] id={run_id}")
    if doc:
        console.print(Markdown(doc))
    if output:
        output.write_text(doc, encoding="utf-8")
        console.print(f"Saved report to {output}")


@app.command("version")
def version_cmd() -> None:
    from manus_agent import __version__

    console.print(__version__)


if __name__ == "__main__":
    app()
