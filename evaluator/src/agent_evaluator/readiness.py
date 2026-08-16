"""Load, model, score, and render the organizational readiness rubric.

``rubric.yaml`` asks how much control a given agent needs. ``readiness.yaml`` — the single source of
truth this module reads — asks the other half: whether the organization running it has that control.
Readiness is never absolute. It is measured against the control level the organization actually
operates, so an organization running only C1 agents can be ready while one running C4 agents with C2
controls is not, however much governance the second has on paper.

Aggregation is deliberately non-compensatory (see ``PD-R-AGG-001``): per dimension, the requirement
is the highest any agent in production triggers, and the achieved level is the *lowest* reached
by an agent that triggers it. No single index value is produced — ``PD-R-AGG-001`` records why.

- ``python -m agent_evaluator.readiness --write``  regenerates the doc blocks from the YAML.
- ``python -m agent_evaluator.readiness --check``  exits non-zero if any doc block is stale.

The consistency test (``tests/test_readiness_consistency.py``) calls :func:`check_docs`.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .regulatory import apply_block, repo_root
from .rubric import LEVEL_ORDER

RUBRIC_DOC = "docs/06-readiness/agent-readiness-rubric.md"


# --------------------------------------------------------------------------- #
# The rubric itself.
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Precondition:
    key: str
    question: str
    on_missing: str


@dataclass(frozen=True)
class ReadinessDimension:
    key: str
    label: str
    question: str
    probe: str
    derived_from: tuple[str, ...]
    anchors: dict[int, str]
    required: dict[str, int]
    self_assessment_caveat: str | None


@dataclass(frozen=True)
class Simplification:
    key: str
    summary: str
    detail: str


@dataclass(frozen=True)
class ReadinessRubric:
    version: int
    title: str
    scale_min: int
    scale_max: int
    preconditions: tuple[Precondition, ...]
    dimensions: tuple[ReadinessDimension, ...]
    aggregation: dict[str, object]
    simplifications: tuple[Simplification, ...]

    @property
    def dimension_keys(self) -> tuple[str, ...]:
        return tuple(d.key for d in self.dimensions)

    def dimension(self, key: str) -> ReadinessDimension:
        for d in self.dimensions:
            if d.key == key:
                return d
        raise ValueError(f"no readiness dimension {key!r}")

    def note(self, name: str) -> str:
        """Return an aggregation note (``known_bias``, ``not_applicable``, …) as clean text."""
        value = self.aggregation.get(name, "")
        return str(value).strip()


def load_readiness_rubric(path: str | Path | None = None) -> ReadinessRubric:
    """Load the rubric from ``path`` (defaults to the packaged ``readiness.yaml``)."""
    if path is None:
        raw = (files("agent_evaluator") / "readiness.yaml").read_text(encoding="utf-8")
    else:
        raw = Path(path).read_text(encoding="utf-8")
    data = yaml.safe_load(raw)

    preconditions = tuple(
        Precondition(
            key=p["key"],
            question=" ".join(p["question"].split()),
            on_missing=" ".join(p["on_missing"].split()),
        )
        for p in data.get("preconditions", [])
    )
    dimensions = tuple(
        ReadinessDimension(
            key=d["key"],
            label=d["label"],
            question=d["question"],
            probe=" ".join(d["probe"].split()),
            derived_from=tuple(d.get("derived_from") or ()),
            anchors={int(k): v for k, v in d["anchors"].items()},
            required={str(k): int(v) for k, v in d["required"].items()},
            self_assessment_caveat=(
                " ".join(d["self_assessment_caveat"].split())
                if d.get("self_assessment_caveat")
                else None
            ),
        )
        for d in data["dimensions"]
    )
    simplifications = tuple(
        Simplification(key=s["key"], summary=s["summary"], detail=" ".join(s["detail"].split()))
        for s in data.get("simplifications", [])
    )
    return ReadinessRubric(
        version=data["version"],
        title=data["title"],
        scale_min=data["scale"]["min"],
        scale_max=data["scale"]["max"],
        preconditions=preconditions,
        dimensions=dimensions,
        aggregation=data["aggregation"],
        simplifications=simplifications,
    )


# --------------------------------------------------------------------------- #
# Scoring — the organization, not the agent.
# --------------------------------------------------------------------------- #
class AgentReadiness(BaseModel):
    """One agent in production: the control level it needs, and the control it actually has."""

    name: str = Field(..., description="Human-readable name of the agent.")
    control_level: str = Field(..., description="Control level from `agent-eval score` (C1–C4).")
    scores: dict[str, int] = Field(..., description="Readiness dimension key → score (R0–R3).")


class OrganizationReadiness(BaseModel):
    """The input to a readiness assessment: every agent the organization runs in production."""

    organization: str
    regulatory_classification_determined: bool = Field(
        default=False,
        description="Has the value-chain role and risk category been determined per agent?",
    )
    agents: list[AgentReadiness] = Field(default_factory=list)


class DimensionResult(BaseModel):
    dimension: str
    label: str
    required: int
    achieved: int
    met: bool
    setting_agents: list[str]
    below_target: list[str]
    agents_short_of_own_requirement: list[str]
    detail: str


class ReadinessResult(BaseModel):
    """The output: a required/achieved pair per dimension, and never a single index value."""

    organization: str
    applicable: bool
    exposure: str | None
    agent_count: int
    dimensions: list[DimensionResult]
    coverage_met: int
    coverage_total: int
    coverage_statement: str
    gaps: list[str]
    warnings: list[str]


def _validate(org: OrganizationReadiness, rubric: ReadinessRubric) -> None:
    expected = set(rubric.dimension_keys)
    for agent in org.agents:
        if agent.control_level not in LEVEL_ORDER:
            raise ValueError(
                f"{agent.name}: control level {agent.control_level!r} is not one of "
                f"{', '.join(LEVEL_ORDER)}"
            )
        missing = expected - set(agent.scores)
        unknown = set(agent.scores) - expected
        if missing:
            raise ValueError(
                f"{agent.name}: missing readiness scores for {', '.join(sorted(missing))}"
            )
        if unknown:
            raise ValueError(f"{agent.name}: unknown dimension(s) {', '.join(sorted(unknown))}")
        for key, value in agent.scores.items():
            if not rubric.scale_min <= value <= rubric.scale_max:
                raise ValueError(
                    f"{agent.name}: readiness score for {key!r} is {value}; must be between "
                    f"R{rubric.scale_min} and R{rubric.scale_max}"
                )


def _not_applicable(org: OrganizationReadiness, rubric: ReadinessRubric) -> ReadinessResult:
    # An organization with no agents in production has no gap by construction. Reporting full
    # coverage here would measure restraint as maturity — see the `not_applicable` note.
    return ReadinessResult(
        organization=org.organization,
        applicable=False,
        exposure=None,
        agent_count=0,
        dimensions=[],
        coverage_met=0,
        coverage_total=0,
        coverage_statement="exposure: none in production — the rubric does not apply",
        gaps=[],
        warnings=[rubric.note("not_applicable")],
    )


def assess_readiness(
    org: OrganizationReadiness, rubric: ReadinessRubric | None = None
) -> ReadinessResult:
    """Assess an organization against the readiness rubric, relative to what it actually runs."""
    rubric = rubric or load_readiness_rubric()
    _validate(org, rubric)
    if not org.agents:
        return _not_applicable(org, rubric)

    exposure = max((a.control_level for a in org.agents), key=LEVEL_ORDER.index)

    results: list[DimensionResult] = []
    gaps: list[str] = []
    for dim in rubric.dimensions:
        required = max(dim.required[a.control_level] for a in org.agents)
        # The agents that set the bar. Achieved is the lowest level reached by one of them: a
        # deliberate minimum, so a strong score on a harmless agent cannot flatter the result.
        setting = [a for a in org.agents if dim.required[a.control_level] == required]
        achieved = min(a.scores[dim.key] for a in setting)
        below = [a.name for a in setting if a.scores[dim.key] < required]
        short = [a.name for a in org.agents if a.scores[dim.key] < dim.required[a.control_level]]
        levels = "/".join(sorted({a.control_level for a in setting}, key=LEVEL_ORDER.index))
        noun = "agent" if len(setting) == 1 else "agents"
        results.append(
            DimensionResult(
                dimension=dim.key,
                label=dim.label,
                required=required,
                achieved=achieved,
                met=achieved >= required,
                setting_agents=[a.name for a in setting],
                below_target=below,
                agents_short_of_own_requirement=short,
                # Always the count, never the bare pair: "1 of 3 C4 agents below target" separates
                # a single site from a systemic gap, which achieved/required alone cannot.
                detail=(
                    f"{len(setting)} {levels} {noun} set the bar"
                    if not below
                    else f"{len(below)} of {len(setting)} {levels} {noun} below target"
                ),
            )
        )
        if achieved < required:
            gaps.append(
                f"{dim.label}: R{achieved} achieved against R{required} required at "
                f"{levels} — {', '.join(below)}"
            )

    met = sum(1 for r in results if r.met)
    return ReadinessResult(
        organization=org.organization,
        applicable=True,
        exposure=exposure,
        agent_count=len(org.agents),
        dimensions=results,
        coverage_met=met,
        coverage_total=len(results),
        coverage_statement=f"{met} of {len(results)} at exposure {exposure}",
        gaps=gaps,
        warnings=_warnings(org, rubric, results),
    )


def _warnings(
    org: OrganizationReadiness, rubric: ReadinessRubric, results: list[DimensionResult]
) -> list[str]:
    warnings: list[str] = []
    if not org.regulatory_classification_determined:
        for precondition in rubric.preconditions:
            warnings.append(f"{precondition.question} {precondition.on_missing}")
    # The caveat only bites where the claim is high: R2 is proven by performing the reconstruction,
    # not by asserting that the log fields exist.
    for result in results:
        caveat = rubric.dimension(result.dimension).self_assessment_caveat
        if caveat and result.achieved >= 2:
            warnings.append(f"{result.label}: {caveat}")
    if len({a.control_level for a in org.agents}) > 1:
        warnings.append(rubric.note("known_bias"))
    # The gaming path, named where it applies: when a single agent sets the exposure, retiring it
    # would lower every figure on this report without one control having improved.
    exposure = max((a.control_level for a in org.agents), key=LEVEL_ORDER.index)
    at_exposure = [a.name for a in org.agents if a.control_level == exposure]
    if len(at_exposure) == 1:
        warnings.append(f"{rubric.note('gaming_path')} Here that agent is {at_exposure[0]}.")
    return warnings


# --------------------------------------------------------------------------- #
# Rendering — one function per generated documentation block.
# --------------------------------------------------------------------------- #
def _render_dimensions(r: ReadinessRubric) -> str:
    parts: list[str] = []
    for d in r.dimensions:
        rows = "\n".join(f"| R{score} | {d.anchors[score]} |" for score in sorted(d.anchors))
        derived = "\n".join(f"- {item}" for item in d.derived_from)
        required = " · ".join(f"{level} → R{d.required[level]}" for level in LEVEL_ORDER)
        block = (
            f"### {d.label}\n\n_{d.question}_\n\n"
            f"| Score | Anchor |\n|:-----:|--------|\n{rows}\n\n"
            f"**Required** — {required}\n\n"
            f"**Probe** — {d.probe}\n\n"
            f"**Derived from**\n\n{derived}"
        )
        if d.self_assessment_caveat:
            block += f"\n\n> **Self-assessment caveat.** {d.self_assessment_caveat}"
        parts.append(block)
    return "\n\n".join(parts)


def _render_required(r: ReadinessRubric) -> str:
    header = "| Dimension | " + " | ".join(LEVEL_ORDER) + " |"
    divider = "|-----------|" + "|".join([":--:"] * len(LEVEL_ORDER)) + "|"
    rows = "\n".join(
        f"| {d.label} | " + " | ".join(f"R{d.required[level]}" for level in LEVEL_ORDER) + " |"
        for d in r.dimensions
    )
    return f"{header}\n{divider}\n{rows}"


def _render_preconditions(r: ReadinessRubric) -> str:
    return "\n\n".join(
        f"**{p.key}** — {p.question}\n\n_If unanswered:_ {p.on_missing}" for p in r.preconditions
    )


def _render_aggregation(r: ReadinessRubric) -> str:
    per_dimension = r.aggregation["per_dimension"]
    lines = [
        f"- **Exposure** — `{r.aggregation['exposure']}`. {r.note('known_bias')}",
        f"- **Required, per dimension** — `{per_dimension['required']}`.",
        f"- **Achieved, per dimension** — `{per_dimension['achieved']}`. {r.note('rationale')}",
        f"- **Coverage** — `{r.aggregation['coverage']}`. {r.note('no_single_score')}",
        f"- **Detail** — {r.note('report_detail')}",
        f"- **Not applicable** — {r.note('not_applicable')}",
        f"- **How this is gamed** — {r.note('gaming_path')}",
    ]
    return "\n".join(lines)


def _render_simplifications(r: ReadinessRubric) -> str:
    return "\n\n".join(f"**{s.summary}**\n\n{s.detail}" for s in r.simplifications)


_RENDERERS = {
    "readiness_preconditions": _render_preconditions,
    "readiness_required": _render_required,
    "readiness_dimensions": _render_dimensions,
    "readiness_aggregation": _render_aggregation,
    "readiness_simplifications": _render_simplifications,
}


def render_block(name: str, rubric: ReadinessRubric | None = None) -> str:
    rubric = rubric or load_readiness_rubric()
    return _RENDERERS[name](rubric)


def update_docs(write: bool, root: Path | None = None) -> list[str]:
    """Regenerate (write=True) or check (write=False) the readiness doc blocks."""
    root = root or repo_root()
    rubric = load_readiness_rubric()
    path = root / RUBRIC_DOC
    original = path.read_text(encoding="utf-8")
    updated = original
    for name in _RENDERERS:
        updated = apply_block(updated, name, render_block(name, rubric))
    if updated == original:
        return []
    if write:
        path.write_text(updated, encoding="utf-8")
    return [RUBRIC_DOC]


def check_docs(root: Path | None = None) -> list[str]:
    """Return the readiness doc if its generated blocks have drifted from the YAML."""
    return update_docs(write=False, root=root)


def _main(argv: list[str]) -> int:
    write = "--write" in argv
    changed = update_docs(write=write)
    if write:
        print("rewrote:", ", ".join(changed) if changed else "nothing (already up to date)")
        return 0
    if changed:
        print("STALE — run `python -m agent_evaluator.readiness --write`:", ", ".join(changed))
        return 1
    print("docs are consistent with readiness.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
