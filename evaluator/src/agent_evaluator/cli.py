"""Command-line entry point for the agent evaluator.

    agent-eval score --input examples/usecase-01-internal-knowledge-assistant.yaml
    agent-eval score --input <file> --json
    agent-eval render-docs        # regenerate the rubric tables in docs/ from rubric.yaml

``policy-check`` and ``log-analyze`` are added in milestone M6.
"""

from __future__ import annotations

import json
from pathlib import Path

import click
import yaml
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from . import __version__
from .risk_score import AgentAssessment, RiskResult, score_agent
from .rubric import load_rubric, update_docs

console = Console()

_LEVEL_STYLE = {"C1": "green", "C2": "yellow", "C3": "dark_orange", "C4": "bold red"}


@click.group()
@click.version_option(__version__, prog_name="agent-eval")
def main() -> None:
    """Governance evaluator for AI agents — risk scoring, policy checks, log analysis."""


@main.command()
def info() -> None:
    """Print what this tool is (and what it is not)."""
    console.print(
        "agent-eval — a reference evaluator for AI-agent governance.\n"
        "Reference pattern, not a framework. Not legal advice."
    )


@main.command()
@click.option(
    "--input",
    "input_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="YAML file with the agent's name and its six dimension scores.",
)
@click.option("--json", "as_json", is_flag=True, help="Emit the result as JSON instead of a table.")
def score(input_path: Path, as_json: bool) -> None:
    """Score a use case and print its risk total, control intensity, and required controls."""
    data = yaml.safe_load(input_path.read_text(encoding="utf-8")) or {}
    try:
        assessment = AgentAssessment(**data)
        result = score_agent(assessment)
    except (ValidationError, ValueError) as exc:
        raise click.ClickException(f"invalid assessment in {input_path}: {exc}") from exc

    if as_json:
        click.echo(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
        return
    _print_result(result)


@main.command("render-docs")
@click.option("--check", is_flag=True, help="Exit non-zero if docs are stale; write nothing.")
def render_docs(check: bool) -> None:
    """Regenerate the rubric tables in docs/ from rubric.yaml (the single source of truth)."""
    changed = update_docs(write=not check)
    if check:
        if changed:
            raise click.ClickException(
                f"stale docs: {', '.join(changed)} — run `agent-eval render-docs`"
            )
        console.print("docs are consistent with rubric.yaml")
    else:
        console.print(f"rewrote: {', '.join(changed)}" if changed else "docs already up to date")


def _print_result(result: RiskResult) -> None:
    rubric = load_rubric()
    anchors = {d.key: d.anchors for d in rubric.dimensions}
    labels = {d.key: d.label for d in rubric.dimensions}

    console.print(f"\n[bold]{result.agent_name}[/bold]")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Dimension")
    table.add_column("Score", justify="center")
    table.add_column("Anchor")
    for key in rubric.dimension_keys:
        value = result.scores[key]
        table.add_row(labels[key], str(value), anchors[key][value])
    console.print(table)

    style = _LEVEL_STYLE.get(result.level, "bold")
    console.print(
        f"Total [bold]{result.total}[/bold] → control intensity "
        f"[{style}]{result.level} ({result.level_name})[/{style}]"
    )
    if result.applied_overrides:
        for ov in result.applied_overrides:
            console.print(f"  • override: {ov.dimension} → floor {ov.floor} ({ov.reason})")

    console.print("\n[bold]Minimum controls[/bold]")
    for control in result.controls:
        console.print(f"  - {control}")

    console.print(f"\n[italic]{result.rationale}[/italic]\n")


if __name__ == "__main__":
    main()
