"""Control-intensity scoring for AI agents.

Implements the rubric documented in ``docs/02-risk-assessment/`` directly from ``rubric.yaml`` —
the single source of truth. Six dimensions, each scored 1-5, sum to a total that falls into a
control-intensity band (C1-C4); an extreme single dimension can then raise the floor.

    >>> from agent_evaluator.risk_score import AgentAssessment, score_agent
    >>> result = score_agent(AgentAssessment(name="demo", scores={
    ...     "autonomy": 3, "action_space": 5, "reversibility": 4,
    ...     "data_sensitivity": 3, "explainability": 3, "blast_radius": 3}))
    >>> result.total, result.level
    (21, 'C4')
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .rubric import LEVEL_ORDER, Band, Rubric, load_rubric


class AgentAssessment(BaseModel):
    """The input to scoring: an agent's identity plus its per-dimension scores."""

    name: str = Field(..., description="Human-readable name of the agent / use case.")
    description: str | None = Field(default=None, description="One-line summary of the use case.")
    scores: dict[str, int] = Field(..., description="Dimension key → score (1-5).")


class AppliedOverride(BaseModel):
    dimension: str
    floor: str
    reason: str


class RiskResult(BaseModel):
    """The output of scoring: total, band, any overrides, the final level, and its controls."""

    agent_name: str
    scores: dict[str, int]
    total: int
    base_level: str
    level: str
    level_name: str
    summary: str
    applied_overrides: list[AppliedOverride]
    controls: list[str]
    rationale: str


def _validate_scores(scores: dict[str, int], rubric: Rubric) -> None:
    expected = set(rubric.dimension_keys)
    got = set(scores)
    missing = expected - got
    unknown = got - expected
    if missing:
        raise ValueError(f"missing scores for: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"unknown dimension(s): {', '.join(sorted(unknown))}")
    for key in rubric.dimension_keys:
        value = scores[key]
        if not rubric.scale_min <= value <= rubric.scale_max:
            raise ValueError(
                f"score for '{key}' is {value}; must be between "
                f"{rubric.scale_min} and {rubric.scale_max}"
            )


def _band_by_level(rubric: Rubric, level: str) -> Band:
    for band in rubric.bands:
        if band.level == level:
            return band
    raise ValueError(f"no band with level {level}")


def score_agent(assessment: AgentAssessment, rubric: Rubric | None = None) -> RiskResult:
    """Score an assessment against the rubric; return the control intensity and its rationale."""
    rubric = rubric or load_rubric()
    _validate_scores(assessment.scores, rubric)

    total = sum(assessment.scores[key] for key in rubric.dimension_keys)
    base_band = rubric.band_for_total(total)

    # Overrides raise the floor; the final level is the highest of the base band and every floor.
    applied: list[AppliedOverride] = []
    for override in rubric.overrides:
        if assessment.scores[override.dimension] >= override.at_least:
            applied.append(
                AppliedOverride(
                    dimension=override.dimension, floor=override.floor, reason=override.reason
                )
            )

    candidate_levels = [base_band.level, *(o.floor for o in applied)]
    final_level = max(candidate_levels, key=LEVEL_ORDER.index)
    final_band = _band_by_level(rubric, final_level)

    rationale = _build_rationale(total, base_band, final_band, applied)

    return RiskResult(
        agent_name=assessment.name,
        scores=dict(assessment.scores),
        total=total,
        base_level=base_band.level,
        level=final_band.level,
        level_name=final_band.name,
        summary=final_band.summary,
        applied_overrides=applied,
        controls=list(rubric.controls.get(final_band.level, ())),
        rationale=rationale,
    )


def _build_rationale(total: int, base: Band, final: Band, applied: list[AppliedOverride]) -> str:
    max_total = 30
    parts = [f"Total {total}/{max_total} places this agent in {base.level} ({base.name})."]
    if final.level != base.level:
        drivers = "; ".join(
            f"{o.dimension.replace('_', ' ')} (→ {o.floor}): {o.reason}" for o in applied
        )
        parts.append(
            f"An override raises the required control intensity to {final.level} ({final.name}) — "
            f"{drivers}"
        )
    parts.append(final.summary)
    return " ".join(parts)
