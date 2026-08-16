"""INV-1, applied to the second rubric — the readiness rubric exists exactly once.

``docs/06-readiness/agent-readiness-rubric.md`` is generated from ``readiness.yaml``. If anyone
edits one without the other, this test fails and names the file to regenerate.

It also guards the structural claims the rubric makes about itself: that every dimension is derived
from a demand the toolkit already makes, that the required level never falls as exposure rises, and
that the demo organization's control levels are the ones the *exposure* rubric actually produces —
so the two rubrics cannot drift apart in the one place a reader compares them.
"""

from __future__ import annotations

import pytest
import yaml

from agent_evaluator import readiness
from agent_evaluator.risk_score import AgentAssessment, score_agent
from agent_evaluator.rubric import LEVEL_ORDER, repo_root

_RUBRIC = readiness.load_readiness_rubric()
_EXAMPLES = repo_root() / "evaluator" / "examples"


def test_docs_match_the_single_source() -> None:
    stale = readiness.check_docs()
    assert stale == [], (
        "documentation has drifted from readiness.yaml: "
        + ", ".join(stale)
        + " — run `agent-eval render-docs`"
    )


def test_render_is_idempotent() -> None:
    assert readiness.update_docs(write=False) == []


def test_every_dimension_and_precondition_is_rendered() -> None:
    dimensions_md = readiness.render_block("readiness_dimensions", _RUBRIC)
    for dim in _RUBRIC.dimensions:
        assert dim.label in dimensions_md
        assert dim.probe in dimensions_md
    preconditions_md = readiness.render_block("readiness_preconditions", _RUBRIC)
    for precondition in _RUBRIC.preconditions:
        assert precondition.key in preconditions_md


@pytest.mark.parametrize("dim", _RUBRIC.dimensions, ids=lambda d: d.key)
def test_every_dimension_records_where_it_comes_from(dim: readiness.ReadinessDimension) -> None:
    # The rubric claims nothing here is invented. `derived_from` is what makes that checkable rather
    # than asserted — a dimension without it would be an opinion wearing a provenance field.
    assert dim.derived_from, f"{dim.key}: no derivation recorded"
    assert dim.probe, f"{dim.key}: no probe — a dimension nobody can ask for evidence about"


@pytest.mark.parametrize("dim", _RUBRIC.dimensions, ids=lambda d: d.key)
def test_anchors_cover_the_whole_scale(dim: readiness.ReadinessDimension) -> None:
    expected = set(range(_RUBRIC.scale_min, _RUBRIC.scale_max + 1))
    assert set(dim.anchors) == expected, f"{dim.key}: anchors {sorted(dim.anchors)} != {expected}"


@pytest.mark.parametrize("dim", _RUBRIC.dimensions, ids=lambda d: d.key)
def test_required_is_defined_for_every_level_and_never_falls(
    dim: readiness.ReadinessDimension,
) -> None:
    assert set(dim.required) == set(LEVEL_ORDER), f"{dim.key}: required {sorted(dim.required)}"
    levels = [dim.required[level] for level in LEVEL_ORDER]
    assert levels == sorted(levels), (
        f"{dim.key}: required falls as exposure rises ({levels}) — a higher control level can "
        "never need less of a dimension than a lower one"
    )
    for level, value in dim.required.items():
        assert _RUBRIC.scale_min <= value <= _RUBRIC.scale_max, f"{dim.key}/{level}: R{value}"


def test_the_demo_organization_uses_the_levels_the_exposure_rubric_produces() -> None:
    # The demo is the one place a reader sees both rubrics at once. If a use case is re-scored and
    # the demo is not, the two disagree in public — so the link is a test, not a convention.
    demo = yaml.safe_load((_EXAMPLES / "org-readiness-demo.yaml").read_text(encoding="utf-8"))
    scored = {}
    for path in sorted(_EXAMPLES.glob("usecase-*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        result = score_agent(AgentAssessment(**data))
        scored[result.agent_name] = result.level

    for agent in demo["agents"]:
        assert agent["name"] in scored, (
            f"{agent['name']} is in the readiness demo but has no scored use case"
        )
        assert agent["control_level"] == scored[agent["name"]], (
            f"{agent['name']}: the demo says {agent['control_level']}, `agent-eval score` says "
            f"{scored[agent['name']]}"
        )
    assert set(scored) == {a["name"] for a in demo["agents"]}, (
        "every scored use case belongs in the readiness demo, or the demo understates the exposure"
    )
