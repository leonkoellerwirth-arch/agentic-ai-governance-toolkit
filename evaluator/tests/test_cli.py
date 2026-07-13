"""The CLI runs — the seed tests that keep the gate green from the first commit."""

from __future__ import annotations

from click.testing import CliRunner

from agent_evaluator import __version__
from agent_evaluator.cli import main


def test_version() -> None:
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_info() -> None:
    result = CliRunner().invoke(main, ["info"])
    assert result.exit_code == 0
    assert "not a framework" in result.output


def test_judge_fixture(judge) -> None:
    assert judge("please escalate this") == "escalate"
    assert judge("looks fine") == "pass"
