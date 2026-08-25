"""Tests for the legal-status record.

The record is a monthly deliverable, and a monthly report that says nothing is read as "nothing
changed". These tests hold the two properties that reading depends on: the record states what it
watched and what it did not, and a check that could not be made is never reported as current.
"""

from __future__ import annotations

from typing import Any

import pytest

from agent_evaluator import legal_status as ls


@pytest.fixture(scope="module")
def record() -> dict[str, Any]:
    return ls.build_record("Beispiel GmbH")


def test_every_pinned_act_appears(record: dict[str, Any]) -> None:
    from agent_evaluator.regulatory import load_sources

    keys = {a["key"] for a in record["acts"]}
    assert keys == {f.key for f in load_sources().frameworks}


def test_the_record_says_what_it_did_not_watch(record: dict[str, Any]) -> None:
    """A record that cannot say what it left out is a promise of completeness nobody can keep."""
    not_covered = record["scope"]["not_covered"]
    assert len(not_covered) >= 4
    joined = " ".join(not_covered).lower()
    for expected in ("national law", "case law", "standards"):
        assert expected in joined, f"the scope does not exclude {expected}"


def test_absence_of_findings_is_explained_not_implied(record: dict[str, Any]) -> None:
    meaning = record["scope"]["meaning_of_no_finding"].lower()
    assert "not a statement that nothing relevant changed" in meaning


def test_an_unreachable_source_is_never_reported_as_current(record: dict[str, Any]) -> None:
    """The failure mode that turns this from evidence into false comfort."""
    assert "never as" in record["scope"]["on_source_failure"].lower()


def test_no_act_is_current_without_a_cited_version(record: dict[str, Any]) -> None:
    for act in record["acts"]:
        if act["status"] == "current":
            assert act["cited_version"], f"{act['key']}: current without naming the version"


def test_a_superseded_pin_is_reported_as_superseded(monkeypatch: pytest.MonkeyPatch) -> None:
    """The finding the whole record exists to produce."""
    real = ls._consolidations()
    faked = {
        "_checked": real.get("_checked"),
        "_source": real.get("_source", "test"),
        "frameworks": {
            key: {**value, "available": [*value["available"], "09999R9999-29991231"]}
            for key, value in real["frameworks"].items()
        },
    }
    monkeypatch.setattr(ls, "_consolidations", lambda: faked)
    record = ls.build_record()
    assert all(a["status"] == "superseded" for a in record["acts"])
    assert all("re-checked" in a["note"] for a in record["acts"])


def test_markdown_carries_the_scope_not_only_the_table(record: dict[str, Any]) -> None:
    """The scope statement is part of the record, not a footnote someone can drop."""
    rendered = ls.render_markdown(record)
    assert "What was watched" in rendered
    assert "What an absence of findings means" in rendered
    for item in record["scope"]["not_covered"]:
        assert item in rendered
