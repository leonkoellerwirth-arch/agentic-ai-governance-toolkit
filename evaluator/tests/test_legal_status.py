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


# --- Registers supplied by the reader --------------------------------------------------------

MACHINERY = """
register: Example register
acts:
  - key: machinery
    act: Machinery Regulation
    celex: 32023R1230
    pinned: 02023R1230-20260727
    why: The products placed on the market are machinery within the meaning of the Regulation.
  - key: ai_act
    act: AI Act
    celex: 32024R1689
    pinned: 02024R1689-20240712
    why: A safety component of that machinery is an AI system.
"""


def _register(tmp_path, text=MACHINERY, name="register.yaml"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _fixed(mapping):
    def resolve(base):
        if base not in mapping:
            raise RuntimeError("no answer")
        return mapping[base]

    return resolve


def test_an_act_without_a_reason_is_not_a_register(tmp_path):
    """A list of acts with no reason per act is a list. The selection is what a reader relies on."""
    text = MACHINERY.replace(
        "    why: The products placed on the market are machinery"
        " within the meaning of the Regulation.\n",
        "",
    )
    with pytest.raises(ls.ProfileError, match="missing why"):
        ls.load_profile(_register(tmp_path, text))


def test_a_pin_from_another_act_is_refused_not_compared(tmp_path):
    """Versions compare as strings. Across works that comparison is meaningless, not wrong."""
    text = MACHINERY.replace("02023R1230-20260727", "02024R1689-20240712")
    with pytest.raises(ls.ProfileError, match="not a consolidation of 32023R1230"):
        ls.load_profile(_register(tmp_path, text))


def test_the_same_act_cannot_be_listed_twice(tmp_path):
    text = MACHINERY + MACHINERY.split("acts:", 1)[1].replace("key: machinery", "key: other")
    with pytest.raises(ls.ProfileError):
        ls.load_profile(_register(tmp_path, text))


def test_an_unreachable_source_is_unchecked_never_current(tmp_path):
    """The one failure mode that turns this record from evidence into false comfort."""
    entries, _ = ls.load_profile(_register(tmp_path))
    statuses = ls.profile_statuses(entries, _fixed({}))
    assert {s.status for s in statuses} == {"unchecked"}
    assert all("could not be reached" in s.note for s in statuses)


def test_a_superseded_pin_in_a_supplied_register_is_found(tmp_path):
    record = ls.build_profile_record(
        _register(tmp_path),
        resolve=_fixed(
            {
                "02023R1230": ["02023R1230-20260727"],
                "02024R1689": ["02024R1689-20240712", "02024R1689-20260727"],
            }
        ),
    )
    by_key = {a["key"]: a for a in record["acts"]}
    assert by_key["machinery"]["status"] == "current"
    assert by_key["ai_act"]["status"] == "superseded"
    assert "02024R1689-20260727" in by_key["ai_act"]["note"]


def test_the_record_says_the_reason_is_not_verified(tmp_path):
    """The reason is the register holder's claim. Presenting it as checked would be the lie."""
    record = ls.build_profile_record(
        _register(tmp_path), resolve=_fixed({"02023R1230": [], "02024R1689": []})
    )
    assert all("not verified by this tool" in a["why_stated_by"] for a in record["acts"])
    assert "does not verify that the selection is complete" in ls.render_markdown(record)


def test_a_supplied_register_is_identified_by_digest(tmp_path):
    """Which selection the record was made against has to survive into the record itself."""
    record = ls.build_profile_record(
        _register(tmp_path), resolve=_fixed({"02023R1230": [], "02024R1689": []})
    )
    assert record["register"]["entries"] == 2
    assert len(record["register"]["sha256"]) == 64
    assert record["schema_version"] == "1.1.0"


def test_the_scope_still_names_what_was_not_watched(tmp_path):
    """A supplied register must not quietly widen the promise the record makes."""
    record = ls.build_profile_record(
        _register(tmp_path), resolve=_fixed({"02023R1230": [], "02024R1689": []})
    )
    assert "national law" in record["scope"]["not_covered"]
    assert "2 acts listed above, and nothing else" in record["scope"]["watched"]
