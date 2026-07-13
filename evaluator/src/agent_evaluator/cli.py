"""Command-line entry point for the agent evaluator.

The ``score`` subcommand is wired in milestone M2 once the risk rubric lands; ``policy-check`` and
``log-analyze`` follow in M6. This module keeps the CLI runnable — and the gate green — from the
first commit.
"""

from __future__ import annotations

import click
from rich.console import Console

from . import __version__

console = Console()


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


if __name__ == "__main__":
    main()
