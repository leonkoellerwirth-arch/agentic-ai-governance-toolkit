"""Tests for the action authority matrix.

The matrix enforces nothing at runtime, which makes its internal consistency the only thing
standing between it and decoration. These tests are that consistency: an escalation to a band
that does not exist, a forbidden row with no evidence, or a matrix in which nothing is actually
forbidden all fail here rather than being read as a stricter rule than they are.
"""

from __future__ import annotations

import copy

import pytest

from agent_evaluator import action_authority as aa
from agent_evaluator.rubric import load_rubric


@pytest.fixture
def matrix() -> aa.Matrix:
    """A throwaway copy, so a test can damage its own."""
    source = aa.load_matrix()
    return aa.Matrix(
        title=source.title,
        authorities=copy.deepcopy(source.authorities),
        groups=copy.deepcopy(source.groups),
        actions=copy.deepcopy(source.actions),
    )


def test_committed_matrix_holds_up() -> None:
    assert aa.check_matrix() == []


def test_every_escalation_names_a_band_that_exists() -> None:
    """The cross-file invariant: escalations point into rubric.yaml, not into the void."""
    levels = {band.level for band in load_rubric().bands}
    for action in aa.load_matrix().actions:
        if escalates := action.get("escalates_at"):
            assert escalates in levels, f"{action['id']} escalates to unknown band {escalates}"


def test_every_row_names_evidence_including_the_forbidden_ones() -> None:
    """A refusal that leaves no trace cannot be audited."""
    for action in aa.load_matrix().actions:
        assert action.get("evidence"), f"{action['id']} has no evidence artifact"


def test_something_is_actually_forbidden() -> None:
    """A matrix where everything passes with enough approval is not a boundary."""
    authorities = {a["authority"] for a in aa.load_matrix().actions}
    assert "forbidden" in authorities


def test_escalation_on_a_forbidden_action_is_caught(matrix: aa.Matrix) -> None:
    forbidden = next(a for a in matrix.actions if a["authority"] == "forbidden")
    forbidden["escalates_at"] = "C3"
    assert any("only applies to an automatic action" in p for p in aa.check_matrix(matrix))


def test_escalation_to_an_unknown_band_is_caught(matrix: aa.Matrix) -> None:
    automatic = next(a for a in matrix.actions if a["authority"] == "automatic")
    automatic["escalates_at"] = "C9"
    assert any("is not a band in rubric.yaml" in p for p in aa.check_matrix(matrix))


def test_missing_evidence_is_caught(matrix: aa.Matrix) -> None:
    matrix.actions[0].pop("evidence")
    assert any("evidence is missing" in p for p in aa.check_matrix(matrix))


def test_missing_rationale_is_caught(matrix: aa.Matrix) -> None:
    """A row without an argument is a preference, and cannot be disagreed with."""
    matrix.actions[0].pop("rationale")
    assert any("rationale is missing" in p for p in aa.check_matrix(matrix))


def test_unknown_authority_is_caught(matrix: aa.Matrix) -> None:
    matrix.actions[0]["authority"] = "probably_fine"
    assert any("is not declared" in p for p in aa.check_matrix(matrix))


def test_duplicate_id_is_caught(matrix: aa.Matrix) -> None:
    matrix.actions.append(copy.deepcopy(matrix.actions[0]))
    assert any("duplicate id" in p for p in aa.check_matrix(matrix))


def test_matrix_with_nothing_forbidden_is_caught(matrix: aa.Matrix) -> None:
    for action in matrix.actions:
        if action["authority"] == "forbidden":
            action["authority"] = "human_approval"
            action.pop("escalates_at", None)
    assert any("not a boundary" in p for p in aa.check_matrix(matrix))


def test_orphan_group_is_caught(matrix: aa.Matrix) -> None:
    matrix.groups.append({"key": "unused", "label": "Unused", "summary": "nothing here"})
    assert any("has no actions" in p for p in aa.check_matrix(matrix))


def test_rendered_matrix_marks_escalation_visibly() -> None:
    """An escalating row must not read as unconditionally automatic."""
    rendered = aa.render_matrix()
    escalating = [a for a in aa.load_matrix().actions if a.get("escalates_at")]
    assert escalating
    for action in escalating:
        assert f"*< {action['escalates_at']}*" in rendered


def test_every_action_appears_in_the_rendered_table() -> None:
    rendered = aa.render_matrix()
    for action in aa.load_matrix().actions:
        assert action["action"] in rendered, f"{action['id']} is not rendered"


def test_render_is_deterministic() -> None:
    assert aa.render_matrix() == aa.render_matrix()
