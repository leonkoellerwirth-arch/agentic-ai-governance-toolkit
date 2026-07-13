"""Rule-based checks of an agent against a machine-readable YAML policy.

Compares an agent's declared attributes — its dimension scores, the data it touches, whether it has
a human in the loop — against the limits in a policy file (see ``policies/example-policy.yaml``) and
reports the violations. The control level is computed with :mod:`agent_evaluator.risk_score`, so the
policy and the rubric stay consistent.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .risk_score import AgentAssessment, score_agent
from .rubric import LEVEL_ORDER, Rubric, load_rubric


class AgentLimits(BaseModel):
    max_scores: dict[str, int] = Field(default_factory=dict)
    allowed_data_categories: list[str] = Field(default_factory=list)
    human_in_the_loop_required_at: str | None = None
    max_control_level: str | None = None


class Policy(BaseModel):
    version: int = 1
    name: str = "policy"
    agent_limits: AgentLimits = Field(default_factory=AgentLimits)
    # log_thresholds are consumed by log_analyzer; kept here so one file holds the whole policy.
    log_thresholds: dict[str, float] = Field(default_factory=dict)


class PolicyCheckInput(BaseModel):
    name: str
    scores: dict[str, int]
    data_categories: list[str] = Field(default_factory=list)
    human_in_the_loop: bool | None = None


class Violation(BaseModel):
    rule: str
    severity: str  # "high" | "medium"
    message: str


class PolicyReport(BaseModel):
    agent_name: str
    policy_name: str
    level: str
    violations: list[Violation]

    @property
    def passed(self) -> bool:
        return not self.violations


def load_policy(path: str | Path) -> Policy:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Policy(**data)


def _level_at_least(level: str, floor: str) -> bool:
    return LEVEL_ORDER.index(level) >= LEVEL_ORDER.index(floor)


def check_policy(
    agent: PolicyCheckInput, policy: Policy, rubric: Rubric | None = None
) -> PolicyReport:
    """Check one agent against one policy and return the violations (empty means it passes)."""
    rubric = rubric or load_rubric()
    result = score_agent(AgentAssessment(name=agent.name, scores=agent.scores), rubric)
    limits = policy.agent_limits
    violations: list[Violation] = []

    # 1. Per-dimension caps.
    for dimension, cap in limits.max_scores.items():
        value = agent.scores.get(dimension)
        if value is not None and value > cap:
            violations.append(
                Violation(
                    rule=f"max_scores.{dimension}",
                    severity="high",
                    message=f"{dimension} is {value}, above the policy cap of {cap} (escalate).",
                )
            )

    # 2. Allowed data categories.
    if limits.allowed_data_categories:
        allowed = set(limits.allowed_data_categories)
        for category in agent.data_categories:
            if category not in allowed:
                violations.append(
                    Violation(
                        rule="allowed_data_categories",
                        severity="high",
                        message=f"data category '{category}' is not permitted by the policy.",
                    )
                )

    # 3. Human-in-the-loop required at/above a level.
    floor = limits.human_in_the_loop_required_at
    if floor and _level_at_least(result.level, floor) and agent.human_in_the_loop is not True:
        violations.append(
            Violation(
                rule="human_in_the_loop_required_at",
                severity="high",
                message=f"level {result.level} requires a human in the loop; none declared.",
            )
        )

    # 4. Maximum control level without escalation.
    ceiling = limits.max_control_level
    if ceiling and not _level_at_least(ceiling, result.level):
        violations.append(
            Violation(
                rule="max_control_level",
                severity="high",
                message=f"level {result.level} exceeds the policy maximum of {ceiling} (escalate).",
            )
        )

    return PolicyReport(
        agent_name=agent.name,
        policy_name=policy.name,
        level=result.level,
        violations=violations,
    )
