"""Scoring, banding, overrides, and input validation."""

from __future__ import annotations

import pytest

from agent_evaluator.risk_score import AgentAssessment, score_agent

# Rubric dimension order: autonomy, action_space, reversibility, data_sensitivity,
# explainability, blast_radius.
_KEYS = (
    "autonomy",
    "action_space",
    "reversibility",
    "data_sensitivity",
    "explainability",
    "blast_radius",
)


def _score(a: int, b: int, c: int, d: int, e: int, f: int):
    return score_agent(
        AgentAssessment(name="t", scores=dict(zip(_KEYS, (a, b, c, d, e, f), strict=True)))
    )


@pytest.mark.parametrize(
    "scores, total, level",
    [
        ((1, 1, 1, 1, 1, 1), 6, "C1"),
        ((4, 1, 1, 1, 2, 1), 10, "C1"),  # top of C1
        ((4, 1, 1, 1, 3, 1), 11, "C2"),  # bottom of C2
        ((4, 4, 4, 1, 2, 1), 16, "C2"),  # top of C2
        ((4, 4, 4, 1, 3, 1), 17, "C3"),  # bottom of C3
        ((4, 4, 4, 4, 3, 3), 22, "C3"),  # top of C3
        ((4, 4, 4, 4, 4, 3), 23, "C4"),  # bottom of C4
        ((5, 4, 4, 4, 4, 4), 25, "C4"),
    ],
)
def test_banding_by_total(scores, total, level) -> None:
    result = _score(*scores)
    assert result.total == total
    assert result.level == level
    assert not result.applied_overrides


def test_action_space_override_forces_c4_from_c1() -> None:
    # Total 10 would be C1, but external payments (action_space=5) force C4.
    result = _score(1, 5, 1, 1, 1, 1)
    assert result.total == 10
    assert result.base_level == "C1"
    assert result.level == "C4"
    assert [o.dimension for o in result.applied_overrides] == ["action_space"]


def test_reversibility_override_forces_at_least_c3() -> None:
    result = _score(1, 1, 5, 1, 1, 1)
    assert result.base_level == "C1"
    assert result.level == "C3"


def test_data_sensitivity_override_forces_at_least_c3() -> None:
    result = _score(1, 1, 1, 5, 1, 1)
    assert result.base_level == "C1"
    assert result.level == "C3"


def test_multiple_overrides_take_the_highest_floor() -> None:
    # action_space=5 → C4, reversibility=5 → C3; the higher floor wins.
    result = _score(1, 5, 5, 1, 1, 1)
    assert result.level == "C4"
    assert {o.dimension for o in result.applied_overrides} == {"action_space", "reversibility"}


def test_override_never_lowers_the_level() -> None:
    # A genuine C4 by score whose only override floor (C3) is lower must stay C4.
    result = _score(5, 4, 5, 4, 4, 4)  # total 26 → C4; reversibility=5 floors to C3
    assert result.total == 26
    assert result.level == "C4"


def test_rationale_explains_an_applied_override() -> None:
    result = _score(1, 5, 1, 1, 1, 1)
    assert "C4" in result.rationale
    assert "override" in result.rationale.lower()


@pytest.mark.parametrize(
    "bad_scores, message",
    [
        ({"autonomy": 1}, "missing scores"),
        ({**dict(zip(_KEYS, [1] * 6, strict=True)), "extra": 3}, "unknown dimension"),
    ],
)
def test_rejects_missing_or_unknown_dimensions(bad_scores, message) -> None:
    with pytest.raises(ValueError, match=message):
        score_agent(AgentAssessment(name="t", scores=bad_scores))


@pytest.mark.parametrize("value", [0, 6, -1])
def test_rejects_out_of_range_scores(value: int) -> None:
    scores = dict(zip(_KEYS, [1] * 6, strict=True))
    scores["autonomy"] = value
    with pytest.raises(ValueError, match="between 1 and 5"):
        score_agent(AgentAssessment(name="t", scores=scores))
