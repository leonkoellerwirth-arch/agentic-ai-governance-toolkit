"""Shared fixtures. Any heavy dependency (a real LLM via Ollama) is faked here so the suite runs
fully offline. Real-model tests are tagged ``@pytest.mark.slow`` and excluded from the gate and CI.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest


class ScriptedJudge:
    """A fake LLM judge: routes by a marker in the prompt and returns a canned verdict."""

    def __init__(self, replies: dict[str, str] | None = None) -> None:
        self._replies = replies or {}

    def __call__(self, prompt: str) -> str:
        for marker, reply in self._replies.items():
            if marker in prompt:
                return reply
        return "pass"


@pytest.fixture
def judge() -> Callable[[str], str]:
    return ScriptedJudge({"escalate": "escalate"})
