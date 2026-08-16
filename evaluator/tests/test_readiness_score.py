"""Readiness scoring — the aggregation rules must behave the way the register says they do.

``PD-R-AGG-001`` claims a non-compensatory minimum and no single index value. ``PD-R-EXPOSURE-001``
claims exposure follows the single riskiest agent. Those are the claims a reader will check, so they
are tested here rather than only written down.
"""

from __future__ import annotations

import pytest
import yaml
from click.testing import CliRunner

from agent_evaluator.cli import main
from agent_evaluator.readiness import (
    AgentReadiness,
    OrganizationReadiness,
    assess_readiness,
    load_readiness_rubric,
)
from agent_evaluator.rubric import repo_root

_RUBRIC = load_readiness_rubric()
_DEMO = repo_root() / "evaluator" / "examples" / "org-readiness-demo.yaml"


def _agent(name: str, level: str, **scores: int) -> AgentReadiness:
    """An agent at R3 everywhere except where the test says otherwise."""
    full = dict.fromkeys(_RUBRIC.dimension_keys, 3)
    full.update(scores)
    return AgentReadiness(name=name, control_level=level, scores=full)


def _assess(*agents: AgentReadiness, classified: bool = True):
    return assess_readiness(
        OrganizationReadiness(
            organization="Test org",
            regulatory_classification_determined=classified,
            agents=list(agents),
        )
    )


# --------------------------------------------------------------------------- #
# The demo, which is what a reader runs first.
# --------------------------------------------------------------------------- #
def test_the_demo_produces_the_documented_result() -> None:
    result = assess_readiness(
        OrganizationReadiness(**yaml.safe_load(_DEMO.read_text(encoding="utf-8")))
    )
    assert result.applicable
    assert result.exposure == "C4"
    assert result.agent_count == 3
    assert (result.coverage_met, result.coverage_total) == (3, 6)
    assert result.coverage_statement == "3 of 6 at exposure C4"
    unmet = {d.dimension for d in result.dimensions if not d.met}
    assert unmet == {"traceability", "containment", "currency"}


def test_the_demo_separates_a_systemic_gap_from_a_single_site() -> None:
    # The whole point of reporting the count: traceability is short at both agents that set the bar,
    # containment at one. A bare achieved/required pair cannot tell those apart.
    result = assess_readiness(
        OrganizationReadiness(**yaml.safe_load(_DEMO.read_text(encoding="utf-8")))
    )
    by_key = {d.dimension: d for d in result.dimensions}
    assert len(by_key["traceability"].below_target) == 2
    assert "2 of 2" in by_key["traceability"].detail
    assert len(by_key["containment"].below_target) == 1
    assert "1 of 1" in by_key["containment"].detail


def test_the_demo_exits_non_zero_so_it_can_gate() -> None:
    result = CliRunner().invoke(main, ["readiness", "--input", str(_DEMO)])
    assert result.exit_code == 1
    assert "3 of 6 at exposure C4" in result.output


# --------------------------------------------------------------------------- #
# PD-R-AGG-001 — the minimum is non-compensatory.
# --------------------------------------------------------------------------- #
def test_a_strong_agent_cannot_compensate_for_a_weak_one_at_the_same_bar() -> None:
    result = _assess(
        _agent("Strong", "C4"),
        _agent("Weak", "C4", containment=0),
    )
    containment = next(d for d in result.dimensions if d.dimension == "containment")
    assert containment.required == 3
    assert containment.achieved == 0, "the mean would have said 1.5; the minimum says 0"
    assert containment.below_target == ["Weak"]
    assert not containment.met


def test_a_harmless_agent_does_not_drag_down_a_bar_it_does_not_set() -> None:
    # Containment requires R0 at C1, so a C1 agent with no stop path at all sets no bar and is not
    # counted against the C4 agent that does.
    result = _assess(
        _agent("Assistant", "C1", containment=0),
        _agent("Payments", "C4"),
    )
    containment = next(d for d in result.dimensions if d.dimension == "containment")
    assert containment.setting_agents == ["Payments"]
    assert containment.achieved == 3
    assert containment.met
    assert containment.agents_short_of_own_requirement == []


def test_an_agent_short_of_its_own_bar_is_recorded_even_when_it_sets_none() -> None:
    # A C1 agent below the C1 requirement is a real gap the organization has, even though the
    # headline pair is set by a riskier agent. It must not vanish from the report.
    result = _assess(
        _agent("Assistant", "C1", inventory=0),
        _agent("Payments", "C4"),
    )
    inventory = next(d for d in result.dimensions if d.dimension == "inventory")
    assert inventory.met, "the bar is set by the C4 agent, which meets it"
    assert inventory.agents_short_of_own_requirement == ["Assistant"]


def test_no_single_index_value_is_produced() -> None:
    # PD-R-AGG-001 refuses a 0-100 score on purpose. This fails if anyone adds one back.
    result = _assess(_agent("Payments", "C4"))
    fields = set(type(result).model_fields)
    assert not fields & {"score", "index", "percentage", "overall", "maturity"}
    assert "at exposure" in result.coverage_statement


# --------------------------------------------------------------------------- #
# PD-R-EXPOSURE-001 — exposure follows the riskiest agent.
# --------------------------------------------------------------------------- #
def test_exposure_is_the_highest_level_in_production() -> None:
    result = _assess(_agent("A", "C1"), _agent("B", "C2"), _agent("C", "C3"))
    assert result.exposure == "C3"


def test_the_gaming_path_is_named_where_it_applies() -> None:
    # Retiring the single riskiest agent lowers the reported exposure without one control having
    # improved. The rubric names that path rather than leaving it to be discovered.
    single = _assess(_agent("Assistant", "C1"), _agent("Payments", "C4"))
    gaming = [w for w in single.warnings if "gamed" in w]
    assert len(gaming) == 1
    assert "Payments" in gaming[0], "the warning must name the agent the figure hangs on"

    shared = _assess(_agent("Payments", "C4"), _agent("Trading", "C4"))
    assert not any("gamed" in w for w in shared.warnings)


def test_a_mixed_estate_is_told_about_the_bias() -> None:
    mixed = _assess(_agent("A", "C1"), _agent("B", "C4"))
    assert any("riskiest agent" in w for w in mixed.warnings)
    uniform = _assess(_agent("A", "C4"), _agent("B", "C4"))
    assert not any("riskiest agent" in w for w in uniform.warnings)


# --------------------------------------------------------------------------- #
# Preconditions, caveats, and the empty estate.
# --------------------------------------------------------------------------- #
def test_an_empty_estate_is_not_applicable_rather_than_fully_covered() -> None:
    # Reporting full coverage here would measure restraint as maturity.
    result = _assess()
    assert not result.applicable
    assert result.exposure is None
    assert (result.coverage_met, result.coverage_total) == (0, 0)
    assert "does not apply" in result.coverage_statement
    assert result.gaps == []


def test_an_undetermined_classification_taints_the_result_rather_than_costing_a_point() -> None:
    unclassified = _assess(_agent("Payments", "C4"), classified=False)
    assert unclassified.coverage_met == 6, "the precondition is not scored"
    assert any("regulatorily incomplete" in w for w in unclassified.warnings)
    classified = _assess(_agent("Payments", "C4"), classified=True)
    assert not any("regulatorily incomplete" in w for w in classified.warnings)


def test_the_self_assessment_caveat_fires_only_where_the_claim_is_high() -> None:
    high = _assess(_agent("Payments", "C4", traceability=2))
    assert any("most reliably overstates" in w for w in high.warnings)
    low = _assess(_agent("Payments", "C4", traceability=1))
    assert not any("most reliably overstates" in w for w in low.warnings)


# --------------------------------------------------------------------------- #
# Input that cannot be scored must say so, not score badly.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("agent", "expected"),
    [
        (
            AgentReadiness(
                name="X", control_level="C5", scores=dict.fromkeys(_RUBRIC.dimension_keys, 1)
            ),
            "not one of",
        ),
        (
            AgentReadiness(name="X", control_level="C1", scores={"inventory": 1}),
            "missing readiness scores",
        ),
        (
            AgentReadiness(
                name="X",
                control_level="C1",
                scores={**dict.fromkeys(_RUBRIC.dimension_keys, 1), "governance_vibes": 3},
            ),
            "unknown dimension",
        ),
        (
            AgentReadiness(
                name="X",
                control_level="C1",
                scores={**dict.fromkeys(_RUBRIC.dimension_keys, 1), "inventory": 7},
            ),
            "must be between",
        ),
    ],
)
def test_unscoreable_input_is_refused_with_a_reason(agent: AgentReadiness, expected: str) -> None:
    with pytest.raises(ValueError, match=expected):
        _assess(agent)
