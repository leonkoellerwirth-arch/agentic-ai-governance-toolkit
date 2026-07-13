"""Policy checks: dimension caps, data categories, HITL, and the control-level ceiling."""

from __future__ import annotations

import yaml

from agent_evaluator.policy_check import (
    AgentLimits,
    Policy,
    PolicyCheckInput,
    check_policy,
    load_policy,
)
from agent_evaluator.rubric import repo_root

_BASE = {
    "autonomy": 2,
    "action_space": 2,
    "reversibility": 2,
    "data_sensitivity": 2,
    "explainability": 2,
    "blast_radius": 2,
}


def _policy() -> Policy:
    return Policy(
        name="test",
        agent_limits=AgentLimits(
            max_scores={"action_space": 4, "data_sensitivity": 4},
            allowed_data_categories=["public", "internal", "personal"],
            human_in_the_loop_required_at="C3",
            max_control_level="C3",
        ),
    )


def test_compliant_agent_passes() -> None:
    agent = PolicyCheckInput(name="ok", scores=_BASE, data_categories=["internal"])
    report = check_policy(agent, _policy())
    assert report.passed
    assert report.violations == []


def test_dimension_cap_violation() -> None:
    agent = PolicyCheckInput(name="x", scores={**_BASE, "action_space": 5}, human_in_the_loop=True)
    rules = {v.rule for v in check_policy(agent, _policy()).violations}
    assert "max_scores.action_space" in rules


def test_disallowed_data_category() -> None:
    agent = PolicyCheckInput(
        name="x", scores=_BASE, data_categories=["special-category"], human_in_the_loop=True
    )
    rules = {v.rule for v in check_policy(agent, _policy()).violations}
    assert "allowed_data_categories" in rules


def test_hitl_required_but_missing() -> None:
    # Scores summing to 18 → C3, without a human in the loop.
    scores = dict.fromkeys(_BASE, 3)
    agent = PolicyCheckInput(name="x", scores=scores, human_in_the_loop=False)
    report = check_policy(agent, _policy())
    assert report.level == "C3"
    assert any(v.rule == "human_in_the_loop_required_at" for v in report.violations)


def test_max_control_level_exceeded() -> None:
    # action_space=5 forces C4, above the policy ceiling of C3.
    agent = PolicyCheckInput(name="x", scores={**_BASE, "action_space": 5}, human_in_the_loop=True)
    report = check_policy(agent, _policy())
    assert report.level == "C4"
    assert any(v.rule == "max_control_level" for v in report.violations)


def test_example_policy_and_agent_files() -> None:
    policy = load_policy(repo_root() / "evaluator" / "policies" / "example-policy.yaml")
    data = yaml.safe_load(
        (repo_root() / "evaluator" / "examples" / "agent-for-policy-check.yaml").read_text("utf-8")
    )
    report = check_policy(PolicyCheckInput(**data), policy)
    rules = {v.rule for v in report.violations}
    assert {
        "max_scores.action_space",
        "human_in_the_loop_required_at",
        "max_control_level",
    } <= rules
