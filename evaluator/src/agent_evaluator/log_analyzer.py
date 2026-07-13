"""Flags an agent's runtime logs against operational thresholds.

Reads a JSONL audit trail in the shape described in ``docs/05-monitoring/logging-requirements.md``,
computes a few risk-relevant rates, and reports where they cross the thresholds a policy defines.
Pure and offline: JSONL in, findings out.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

# Data categories that must never be touched by an out-of-scope action without being flagged.
SENSITIVE_CATEGORIES = frozenset({"personal", "special-category", "secrets"})


class LogMetrics(BaseModel):
    total_events: int
    tasks: int
    actions: int
    escalations: int
    errors: int
    blocked: int
    sensitive_out_of_scope: int
    escalation_rate: float
    error_rate: float
    blocked_action_rate: float


class Finding(BaseModel):
    metric: str
    value: float
    threshold: float
    message: str


class LogAnalysis(BaseModel):
    metrics: LogMetrics
    findings: list[Finding] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.findings


def parse_events(text: str) -> list[dict]:
    """Parse a JSONL audit trail; blank lines are skipped, a malformed line names its number."""
    events: list[dict] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {lineno}: {exc}") from exc
    return events


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def compute_metrics(events: list[dict]) -> LogMetrics:
    run_ids = {e.get("run_id") for e in events if e.get("run_id") is not None}
    tasks = len(run_ids) or sum(1 for e in events if e.get("event_type") in {"plan", "action"})
    actions = sum(1 for e in events if e.get("event_type") == "action")
    escalations = sum(
        1 for e in events if e.get("event_type") == "escalation" or e.get("outcome") == "escalated"
    )
    errors = sum(1 for e in events if e.get("event_type") == "error" or e.get("outcome") == "error")
    blocked = sum(
        1 for e in events if e.get("outcome") == "blocked" or e.get("action_in_scope") is False
    )
    sensitive_out_of_scope = sum(
        1
        for e in events
        if e.get("action_in_scope") is False
        and SENSITIVE_CATEGORIES.intersection(e.get("data_categories", []))
    )
    return LogMetrics(
        total_events=len(events),
        tasks=tasks,
        actions=actions,
        escalations=escalations,
        errors=errors,
        blocked=blocked,
        sensitive_out_of_scope=sensitive_out_of_scope,
        escalation_rate=_rate(escalations, tasks),
        error_rate=_rate(errors, tasks),
        blocked_action_rate=_rate(blocked, actions),
    )


# threshold key → (metric attribute, comparison label)
_THRESHOLD_METRICS = {
    "escalation_rate_max": ("escalation_rate", "escalation rate"),
    "error_rate_max": ("error_rate", "error rate"),
    "blocked_action_rate_max": ("blocked_action_rate", "blocked-action rate"),
    "sensitive_out_of_scope_events_max": ("sensitive_out_of_scope", "sensitive out-of-scope"),
}


def analyze_logs(events: list[dict], thresholds: dict[str, float]) -> LogAnalysis:
    """Compute metrics and flag every threshold the logs exceed."""
    metrics = compute_metrics(events)
    findings: list[Finding] = []
    for key, (attr, label) in _THRESHOLD_METRICS.items():
        if key not in thresholds:
            continue
        limit = float(thresholds[key])
        value = float(getattr(metrics, attr))
        if value > limit:
            findings.append(
                Finding(
                    metric=attr,
                    value=value,
                    threshold=limit,
                    message=f"{label} is {value}, above the threshold of {limit}.",
                )
            )
    return LogAnalysis(metrics=metrics, findings=findings)


def analyze_log_file(path: str | Path, thresholds: dict[str, float]) -> LogAnalysis:
    events = parse_events(Path(path).read_text(encoding="utf-8"))
    return analyze_logs(events, thresholds)
