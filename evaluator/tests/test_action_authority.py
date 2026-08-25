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
from agent_evaluator.policy import check_coverage, required_targets


@pytest.fixture
def matrix() -> aa.Matrix:
    """A throwaway copy, so a test can damage its own."""
    source = aa.load_matrix()
    return aa.Matrix(
        title=source.title,
        forbidden_criterion=source.forbidden_criterion,
        authorities=copy.deepcopy(source.authorities),
        groups=copy.deepcopy(source.groups),
        actions=copy.deepcopy(source.actions),
    )


def test_committed_matrix_holds_up() -> None:
    assert aa.check_matrix() == []


def test_authority_never_depends_on_the_control_band() -> None:
    """The correction this file exists after: a band is a sum, not a property of an action."""
    for action in aa.load_matrix().actions:
        assert "escalates_at" not in action, (
            f"{action['id']} couples authority to a control band — a system holding personal "
            "data can score C1, and C3 can arise with none in it"
        )


def test_every_automatic_action_states_its_preconditions() -> None:
    """Blanket permission is the failure this matrix exists to make visible."""
    for action in aa.load_matrix().actions:
        if action["authority"] == "automatic":
            assert action.get("automatic_requires"), f"{action['id']} is automatic unconditionally"


def test_the_judgements_are_registered_under_inv_6() -> None:
    """Unregistered thresholds are personal preference wearing governance vocabulary."""
    targets = required_targets()
    for suffix in ("#authorities", "#forbidden_criterion", "#conditions"):
        assert f"action_authority.yaml{suffix}" in targets
    assert check_coverage() == []


def test_a_forbidden_action_carries_no_conditions(matrix: aa.Matrix) -> None:
    """A condition on a refusal is an approval with extra steps."""
    forbidden = next(a for a in matrix.actions if a["authority"] == "forbidden")
    forbidden["automatic_if"] = ["if it seems fine"]
    assert any("does not apply to a 'forbidden' action" in p for p in aa.check_matrix(matrix))


def test_missing_forbidden_criterion_is_caught(matrix: aa.Matrix) -> None:
    stripped = aa.Matrix(
        title=matrix.title,
        forbidden_criterion="  ",
        authorities=matrix.authorities,
        groups=matrix.groups,
        actions=matrix.actions,
    )
    assert any("forbidden_criterion is missing" in p for p in aa.check_matrix(stripped))


def test_every_row_names_evidence_including_the_forbidden_ones() -> None:
    """A refusal that leaves no trace cannot be audited."""
    for action in aa.load_matrix().actions:
        assert action.get("evidence"), f"{action['id']} has no evidence artifact"


def test_something_is_actually_forbidden() -> None:
    """A matrix where everything passes with enough approval is not a boundary."""
    authorities = {a["authority"] for a in aa.load_matrix().actions}
    assert "forbidden" in authorities


def test_unconditional_automatic_is_caught(matrix: aa.Matrix) -> None:
    automatic = next(a for a in matrix.actions if a["authority"] == "automatic")
    automatic.pop("automatic_requires")
    assert any("needs at least one precondition" in p for p in aa.check_matrix(matrix))


def test_carve_out_on_an_automatic_action_is_caught(matrix: aa.Matrix) -> None:
    """`automatic_if` is the exception for an action that normally needs approval."""
    automatic = next(a for a in matrix.actions if a["authority"] == "automatic")
    automatic["automatic_if"] = ["already automatic"]
    assert any("does not apply to a 'automatic' action" in p for p in aa.check_matrix(matrix))


def test_decision_and_execution_are_separate_rows() -> None:
    """The correction Codex found: forbidding both halves forbids the compliant path."""
    ids = {a["id"]: a["authority"] for a in aa.load_matrix().actions}
    assert ids["execute-deletion-rule"] == "automatic"
    assert ids["decide-deletion"] == "forbidden"
    assert ids["revoke-access"] == "automatic"
    assert ids["grant-access"] == "human_approval"
    assert ids["initiate-payment"] == "human_approval"


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


def test_rendered_matrix_marks_conditional_rows_visibly() -> None:
    """A conditional row must not read as unconditional permission."""
    rendered = aa.render_matrix()
    conditional = [
        a for a in aa.load_matrix().actions if any(a.get(f) for f in aa.CONDITION_FIELDS)
    ]
    assert conditional
    assert "\u2009*" in rendered


def test_every_condition_appears_in_the_rationales() -> None:
    """A precondition that is not rendered is a rule nobody can follow."""
    rendered = aa.render_rationales()
    for action in aa.load_matrix().actions:
        for field in aa.CONDITION_FIELDS:
            for condition in action.get(field, []) or []:
                assert " ".join(str(condition).split()) in rendered


def test_every_action_appears_in_the_rendered_table() -> None:
    rendered = aa.render_matrix()
    for action in aa.load_matrix().actions:
        assert action["action"] in rendered, f"{action['id']} is not rendered"


def test_render_is_deterministic() -> None:
    assert aa.render_matrix() == aa.render_matrix()
