"""The LLM-judge pattern, exercised offline with a scripted backend (no real model)."""

from __future__ import annotations

import importlib.util

import pytest

from agent_evaluator.llm_judge import (
    JudgeUnavailable,
    build_prompt,
    judge_output,
    ollama_backend,
    parse_verdict,
)


def test_prompt_contains_policy_and_output() -> None:
    prompt = build_prompt("did a thing", "no external payments")
    assert "no external payments" in prompt
    assert "did a thing" in prompt


@pytest.mark.parametrize(
    "raw, decision",
    [
        ("PASS\nlooks fine", "pass"),
        ("ESCALATE\nneeds a human", "escalate"),
        ("REJECT\nviolates policy", "reject"),
        ("I am not sure about this", "escalate"),  # unclear fails safe to escalate
    ],
)
def test_parse_verdict(raw: str, decision: str) -> None:
    assert parse_verdict(raw).decision == decision


def test_judge_output_with_scripted_backend() -> None:
    backend = lambda prompt: "REJECT\nthe output moves money without approval"  # noqa: E731
    verdict = judge_output("pay supplier 10000", "no external payments", backend=backend)
    assert verdict.decision == "reject"
    assert "money" in verdict.reason


@pytest.mark.skipif(
    importlib.util.find_spec("ollama") is not None, reason="ollama installed; backend is available"
)
def test_ollama_backend_unavailable_without_extra() -> None:
    with pytest.raises(JudgeUnavailable):
        ollama_backend()
