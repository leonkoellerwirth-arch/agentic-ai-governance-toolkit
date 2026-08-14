"""INV-6 — every threshold is derived or decided, never merely present.

A number in a rubric that nobody can account for is indistinguishable from a number nobody thought
about. These tests fail if a threshold has no recorded decision, if a decision points at a threshold
that no longer exists, or if the register doc drifts from the YAML.
"""

from __future__ import annotations

import pytest

from agent_evaluator import policy


def test_every_threshold_is_accounted_for() -> None:
    problems = policy.check_coverage()
    assert problems == [], "thresholds and decisions disagree:\n" + "\n".join(problems)


def test_docs_match_the_register() -> None:
    stale = policy.check_docs()
    assert stale == [], (
        "documentation has drifted from policy_decisions.yaml: "
        + ", ".join(stale)
        + " — run `agent-eval render-docs`"
    )


def test_render_is_idempotent() -> None:
    assert policy.update_docs(write=False) == []


def test_the_thresholds_needing_cover_come_from_the_rubric() -> None:
    # Not a hand-maintained list: bands and overrides are read off rubric.yaml, so a new override
    # demands a new decision without anyone remembering to add it here.
    required = policy.required_targets()
    assert "rubric.yaml#aggregation.bands" in required
    assert "rubric.yaml#aggregation.overrides.action_space" in required
    assert len(required) == len(set(required)), "a threshold is required twice"


@pytest.mark.parametrize("decision", policy.load_register().decisions, ids=lambda d: d.id)
def test_each_decision_states_its_reasoning_and_its_cost(decision: policy.Decision) -> None:
    # A decision without an accepted cost is a justification, not a decision. The cost is the part
    # that is uncomfortable to write and the part a reviewer actually needs.
    assert decision.rationale, f"{decision.id}: no reasoning recorded"
    assert len(decision.accepted_cost) > 40, f"{decision.id}: no meaningful accepted cost recorded"
    assert decision.status == "project_policy", (
        f"{decision.id}: status {decision.status!r} — a project decision must not claim to be more"
    )


def test_unsupported_decisions_say_so_rather_than_inventing_a_citation() -> None:
    # An empty external_support is the honest state for most of these. What must never happen is a
    # citation that does not support the specific threshold — see the review of this concept.
    register = policy.load_register()
    assert any(not d.external_support for d in register.decisions)
