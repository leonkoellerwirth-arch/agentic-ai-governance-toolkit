"""The worked examples in docs/02 are backed by runnable inputs producing the documented levels."""

from __future__ import annotations

import yaml

from agent_evaluator.risk_score import AgentAssessment, score_agent
from agent_evaluator.rubric import repo_root

_EXAMPLES = repo_root() / "evaluator" / "examples"

# filename stem → (expected total, expected final level, override expected?)
_EXPECTED = {
    "usecase-01-internal-knowledge-assistant": (10, "C1", False),
    "usecase-02-customer-servicing-agent": (18, "C3", False),
    "usecase-03-payments-operations-agent": (21, "C4", True),
}


def test_example_inputs_exist() -> None:
    found = {p.stem for p in _EXAMPLES.glob("usecase-*.yaml")}
    assert found == set(_EXPECTED), f"example set changed: {found}"


def test_examples_score_as_documented() -> None:
    for stem, (total, level, has_override) in _EXPECTED.items():
        data = yaml.safe_load((_EXAMPLES / f"{stem}.yaml").read_text(encoding="utf-8"))
        result = score_agent(AgentAssessment(**data))
        assert result.total == total, f"{stem}: total {result.total} != {total}"
        assert result.level == level, f"{stem}: level {result.level} != {level}"
        assert bool(result.applied_overrides) == has_override, stem
