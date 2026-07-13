"""Log analysis: metric computation, threshold findings, and JSONL parsing."""

from __future__ import annotations

import pytest

from agent_evaluator.log_analyzer import (
    analyze_log_file,
    analyze_logs,
    compute_metrics,
    parse_events,
)
from agent_evaluator.policy_check import load_policy
from agent_evaluator.rubric import repo_root

_EVENTS = [
    {"run_id": "r-1", "event_type": "action", "action_in_scope": True, "outcome": "success"},
    {"run_id": "r-2", "event_type": "action", "action_in_scope": True, "outcome": "success"},
    {"run_id": "r-3", "event_type": "escalation", "outcome": "escalated"},
    {
        "run_id": "r-4",
        "event_type": "action",
        "action_in_scope": False,
        "outcome": "blocked",
        "data_categories": ["personal"],
    },
    {"run_id": "r-5", "event_type": "error", "outcome": "error"},
]


def test_metrics() -> None:
    m = compute_metrics(_EVENTS)
    assert m.tasks == 5
    assert m.actions == 3
    assert m.escalations == 1
    assert m.errors == 1
    assert m.blocked == 1
    assert m.sensitive_out_of_scope == 1
    assert m.escalation_rate == 0.2
    assert m.error_rate == 0.2
    assert m.blocked_action_rate == pytest.approx(1 / 3, abs=1e-4)


def test_findings_flag_exceeded_thresholds() -> None:
    thresholds = {
        "escalation_rate_max": 0.30,
        "error_rate_max": 0.05,
        "blocked_action_rate_max": 0.10,
        "sensitive_out_of_scope_events_max": 0,
    }
    analysis = analyze_logs(_EVENTS, thresholds)
    flagged = {f.metric for f in analysis.findings}
    assert flagged == {"error_rate", "blocked_action_rate", "sensitive_out_of_scope"}
    assert not analysis.passed


def test_no_thresholds_means_no_findings() -> None:
    assert analyze_logs(_EVENTS, {}).passed


def test_parse_skips_blank_lines_and_rejects_bad_json() -> None:
    assert parse_events('{"a": 1}\n\n  \n{"b": 2}\n') == [{"a": 1}, {"b": 2}]
    with pytest.raises(ValueError, match="line 1"):
        parse_events("{not json}")


def test_example_log_file() -> None:
    thresholds = load_policy(
        repo_root() / "evaluator" / "policies" / "example-policy.yaml"
    ).log_thresholds
    analysis = analyze_log_file(
        repo_root() / "evaluator" / "examples" / "logs-sample.jsonl", thresholds
    )
    flagged = {f.metric for f in analysis.findings}
    assert "sensitive_out_of_scope" in flagged
    assert "escalation_rate" not in flagged  # 0.2 is within the 0.30 threshold
