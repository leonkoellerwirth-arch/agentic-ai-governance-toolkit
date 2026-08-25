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
from .action_authority import check_matrix
from .action_authority import update_docs as update_authority_docs
from .evidence import write_manifest
from .legal_status import build_record, render_markdown
from .llm_judge import JudgeUnavailable, judge_output
from .log_analyzer import analyze_log_file
from .policy import check_coverage
from .policy import update_docs as update_policy_docs
from .policy_check import PolicyCheckInput, check_policy, load_policy
from .readiness import OrganizationReadiness, ReadinessResult, assess_readiness
from .readiness import update_docs as update_readiness_docs
from .regulatory import check_references
from .regulatory import update_docs as update_regulatory_docs
from .risk_score import AgentAssessment, RiskResult, score_agent
from .rubric import load_rubric, update_docs

console = Console()

_LEVEL_STYLE = {"C1": "green", "C2": "yellow", "C3": "dark_orange", "C4": "bold red"}


@click.group()
@click.version_option(__version__, prog_name="agent-eval")
def main() -> None:
    """Governance evaluator for AI agents — risk scoring, policy checks, log analysis."""


@main.command()
@click.option(
    "--evidence",
    "evidence_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory of evidence files written by a gate run.",
)
@click.option("--commit", default="", help="Commit the run was made against, if known.")
def manifest(evidence_dir: Path, commit: str) -> None:
    """Describe a directory of evidence: tool, rulesets, commit, and a digest per file."""
    target = write_manifest(evidence_dir, commit=commit)
    console.print(f"wrote {target}")


@main.command("legal-status")
@click.option("--for", "prepared_for", default="", help="Who the record is prepared for.")
@click.option("--json", "as_json", is_flag=True, help="Emit the record as JSON.")
def legal_status(prepared_for: str, as_json: bool) -> None:
    """State, for every pinned act, whether the cited version is still the newest known."""
    record = build_record(prepared_for)
    if as_json:
        click.echo(json.dumps(record, indent=2, ensure_ascii=False))
    else:
        click.echo(render_markdown(record))
    if any(a["status"] == "superseded" for a in record["acts"]):
        raise SystemExit(1)


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


@main.command()
@click.option(
    "--input",
    "input_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="YAML listing every agent in production with its control level and R0–R3 scores.",
)
@click.option("--json", "as_json", is_flag=True, help="Emit the assessment as JSON.")
def readiness(input_path: Path, as_json: bool) -> None:
    """Assess whether the organization can carry the exposure it runs; exit non-zero on any gap."""
    data = yaml.safe_load(input_path.read_text(encoding="utf-8")) or {}
    try:
        result = assess_readiness(OrganizationReadiness(**data))
    except (ValidationError, ValueError) as exc:
        raise click.ClickException(f"invalid readiness input in {input_path}: {exc}") from exc

    if as_json:
        click.echo(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
    else:
        _print_readiness(result)
    if result.gaps:
        raise SystemExit(1)


@main.command("render-docs")
@click.option("--check", is_flag=True, help="Exit non-zero if docs are stale; write nothing.")
def render_docs(check: bool) -> None:
    """Regenerate the generated doc blocks from rubric.yaml and regulatory_sources.yaml."""
    if boundary := check_matrix():
        raise click.ClickException(
            "the action authority matrix does not hold up:\n  " + "\n  ".join(boundary)
        )
    changed = (
        update_docs(write=not check)
        + update_regulatory_docs(write=not check)
        + update_policy_docs(write=not check)
        + update_readiness_docs(write=not check)
        + update_authority_docs(write=not check)
    )
    unpinned = check_references()
    if unpinned:
        raise click.ClickException(
            "regulatory references are not pinned to regulatory_sources.yaml:\n  "
            + "\n  ".join(unpinned)
        )
    uncovered = check_coverage()
    if uncovered:
        raise click.ClickException(
            "rubric thresholds without a recorded decision:\n  " + "\n  ".join(uncovered)
        )
    if check:
        if changed:
            raise click.ClickException(
                f"stale docs: {', '.join(changed)} — run `agent-eval render-docs`"
            )
        console.print(
            "docs are consistent with rubric.yaml, readiness.yaml, regulatory_sources.yaml, "
            "policy_decisions.yaml, and action_authority.yaml"
        )
    else:
        console.print(f"rewrote: {', '.join(changed)}" if changed else "docs already up to date")


@main.command("policy-check")
@click.option(
    "--input",
    "input_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="YAML with the agent's name, scores, data_categories, and human_in_the_loop.",
)
@click.option(
    "--policy",
    "policy_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="YAML policy file (see policies/example-policy.yaml).",
)
@click.option("--json", "as_json", is_flag=True, help="Emit the report as JSON.")
def policy_check(input_path: Path, policy_path: Path, as_json: bool) -> None:
    """Check an agent against a policy; exit non-zero if it has any violations."""
    data = yaml.safe_load(input_path.read_text(encoding="utf-8")) or {}
    try:
        report = check_policy(PolicyCheckInput(**data), load_policy(policy_path))
    except (ValueError, TypeError) as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
    else:
        console.print(f"\n[bold]{report.agent_name}[/bold] vs policy '{report.policy_name}'")
        console.print(f"Control level: {report.level}")
        if report.passed:
            console.print("[green]No policy violations.[/green]\n")
        else:
            for v in report.violations:
                console.print(f"  [red]✗[/red] [{v.severity}] {v.rule}: {v.message}")
            console.print()
    if not report.passed:
        raise SystemExit(1)


@main.command("log-analyze")
@click.option(
    "--input",
    "input_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="JSONL audit trail (one event per line).",
)
@click.option(
    "--policy",
    "policy_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="YAML policy file with a log_thresholds section.",
)
@click.option("--json", "as_json", is_flag=True, help="Emit the analysis as JSON.")
def log_analyze(input_path: Path, policy_path: Path, as_json: bool) -> None:
    """Analyze an agent's logs against policy thresholds; exit non-zero on any finding."""
    thresholds = load_policy(policy_path).log_thresholds
    try:
        analysis = analyze_log_file(input_path, thresholds)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(analysis.model_dump(), indent=2, ensure_ascii=False))
    else:
        m = analysis.metrics
        console.print(
            f"\n[bold]Logs[/bold]: {m.total_events} events, {m.tasks} tasks — "
            f"escalation {m.escalation_rate}, error {m.error_rate}, blocked {m.blocked_action_rate}"
        )
        if analysis.passed:
            console.print("[green]Within all thresholds.[/green]\n")
        else:
            for f in analysis.findings:
                console.print(f"  [red]✗[/red] {f.message}")
            console.print()
    if not analysis.passed:
        raise SystemExit(1)


@main.command()
@click.option(
    "--output",
    "output_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Text file with the agent output to judge.",
)
@click.option(
    "--policy",
    "policy_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="YAML policy file; its name and limits form the policy summary.",
)
def judge(output_path: Path, policy_path: Path) -> None:
    """OPTIONAL: judge an agent output with a local LLM (Ollama). A pattern, not production."""
    policy = load_policy(policy_path)
    summary = f"{policy.name}: {policy.agent_limits.model_dump()}"
    try:
        verdict = judge_output(output_path.read_text(encoding="utf-8"), summary)
    except JudgeUnavailable as exc:
        raise click.ClickException(str(exc)) from exc
    console.print(f"[bold]{verdict.decision.upper()}[/bold] — {verdict.reason}")
    if verdict.decision != "pass":
        raise SystemExit(1)


def _print_readiness(result: ReadinessResult) -> None:
    console.print(f"\n[bold]{result.organization}[/bold]")
    if not result.applicable:
        console.print(f"[yellow]{result.coverage_statement}[/yellow]")
        for warning in result.warnings:
            console.print(f"  [yellow]![/yellow] {warning}")
        console.print()
        return

    style = _LEVEL_STYLE.get(result.exposure or "", "bold")
    console.print(
        f"Exposure [{style}]{result.exposure}[/{style}] — the highest control level among "
        f"{result.agent_count} agents in production"
    )

    table = Table(show_header=True, header_style="bold")
    table.add_column("Dimension")
    table.add_column("Required", justify="center")
    table.add_column("Achieved", justify="center")
    table.add_column("", justify="center")
    table.add_column("Agents setting the bar")
    for d in result.dimensions:
        mark = "[green]✓[/green]" if d.met else "[red]✗[/red]"
        achieved = f"R{d.achieved}" if d.met else f"[red]R{d.achieved}[/red]"
        table.add_row(d.label, f"R{d.required}", achieved, mark, d.detail)
    console.print(table)

    # Deliberately not a single index value: the pair per dimension cannot be quoted without its
    # exposure, and a number invites optimizing the number instead of the control.
    console.print(f"Coverage [bold]{result.coverage_statement}[/bold]")

    if result.gaps:
        console.print("\n[bold]Gaps[/bold]")
        for gap in result.gaps:
            console.print(f"  [red]✗[/red] {gap}")
    for warning in result.warnings:
        console.print(f"\n[yellow]![/yellow] {warning}")
    console.print()


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
