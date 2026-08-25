"""Tests for the legal-status record.

The record is a monthly deliverable, and a monthly report that says nothing is read as "nothing
changed". These tests hold the two properties that reading depends on: the record states what it
watched and what it did not, and a check that could not be made is never reported as current.
"""

from __future__ import annotations

from typing import Any

import pytest

from agent_evaluator import celex
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


REAL = {
    "02023R1230": ["02023R1230-20260727"],
    "02024R1689": ["02024R1689-20240712"],
}


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
    entries, _, _ = ls.load_profile(_register(tmp_path))
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
    record = ls.build_profile_record(_register(tmp_path), resolve=_fixed(REAL))
    assert all("not verified by this tool" in a["why_stated_by"] for a in record["acts"])
    assert "does not verify that the selection is complete" in ls.render_markdown(record)


def test_a_supplied_register_is_identified_by_digest(tmp_path):
    """Which selection the record was made against has to survive into the record itself."""
    record = ls.build_profile_record(_register(tmp_path), resolve=_fixed(REAL))
    assert record["register"]["entries"] == 2
    assert len(record["register"]["sha256"]) == 64
    assert record["schema_version"] == ls.SCHEMA_VERSION


def test_the_scope_still_names_what_was_not_watched(tmp_path):
    """A supplied register must not quietly widen the promise the record makes."""
    record = ls.build_profile_record(_register(tmp_path), resolve=_fixed(REAL))
    assert "national law" in record["scope"]["not_covered"]
    assert "2 acts listed above, and nothing else" in record["scope"]["watched"]


# --- Rendering in another language -------------------------------------------------------------


def test_every_finding_can_be_stated_in_every_language():
    """A finding that exists only in English cannot be put in front of a German reader."""
    for lang in ls.LANGUAGES:
        assert set(ls.NOTES[lang]) == set(ls.NOTES["en"]), f"{lang} is missing a finding"


def test_every_excluded_area_can_be_named_in_german():
    """The scope statement is the part that must not thin out in translation."""
    assert set(ls.NOT_COVERED) == set(ls.NOT_COVERED_DE)


def test_every_scaffolding_phrase_exists_in_every_language():
    for lang in ls.LANGUAGES:
        assert set(ls.WORDS[lang]) == set(ls.WORDS["en"]), f"{lang} is missing a phrase"


def test_the_judgement_only_produces_findings_that_exist(tmp_path):
    """assess() is the only place the two versions are compared; its keys must all be renderable."""
    both = ["02024R1689-20240712", "02024R1689-20260727"]
    cases = [
        (None, []),
        (None, both),
        ("02024R1689-20240712", []),
        ("02024R1689-20240712", both),
        ("02024R1689-20260727", both),
        ("02024R1689-20991231", both),
    ]
    for pinned, available in cases:
        _, key, args = ls.assess(pinned, available)
        assert key in ls.NOTES["en"]
        for lang in ls.LANGUAGES:
            ls.note_text(key, args, lang)  # raises on a missing placeholder


def test_the_german_record_still_says_what_it_did_not_watch(tmp_path):
    """Translating away the limits would be the one change that makes the record dishonest."""
    record = ls.build_profile_record(_register(tmp_path), resolve=_fixed(REAL))
    german = ls.render_markdown(record, "de")
    assert "nationales Recht" in german
    assert "Rechtsprechung" in german
    assert "nie als aktuell" in german
    assert "keine Aussage darüber, dass sich nichts Relevantes geändert hat" in german


def test_the_german_record_carries_no_english_scaffolding(tmp_path):
    record = ls.build_profile_record(_register(tmp_path), resolve=_fixed(REAL))
    german = ls.render_markdown(record, "de")
    for leak in ("Not covered", "What was watched", "Legal status record", "Source last checked"):
        assert leak not in german, f"{leak!r} survived into the German record"


def test_an_unknown_language_is_refused_not_silently_english():
    with pytest.raises(ValueError, match="no rendering"):
        ls.render_markdown(ls.build_record(), "fr")


# --- What was deliberately left out ------------------------------------------------------------

EXCLUDED = """
excluded:
  - act: Verordnung (EU) 2023/988 (Produktsicherheit)
    celex: 32023R0988
    why_not: Greift subsidiär für Verbraucherprodukte; der Vertrieb ist rein B2B.
    revisit_when: Maschinen auch an Verbraucher abgegeben werden.
  - act: ATEX-Richtlinie 2014/34/EU
    why_not: Nur bei Geräten für explosionsgefährdete Bereiche.
"""


def test_an_exclusion_without_a_reason_is_refused(tmp_path):
    """An act dropped without a recorded reason is indistinguishable from one nobody thought of."""
    text = MACHINERY + EXCLUDED.replace(
        "    why_not: Nur bei Geräten für explosionsgefährdete Bereiche.\n", ""
    )
    with pytest.raises(ls.ProfileError, match="missing why_not"):
        ls.load_profile(_register(tmp_path, text))


def test_an_act_cannot_be_both_watched_and_excluded(tmp_path):
    """Rendering the contradiction would leave the reader to pick which half to believe."""
    text = MACHINERY + EXCLUDED.replace("32023R0988", "32024R1689")
    with pytest.raises(ls.ProfileError, match="both listed and excluded"):
        ls.load_profile(_register(tmp_path, text))


def test_an_exclusion_is_never_version_checked(tmp_path):
    """Checking it would report currency for an act the register does not claim to watch."""
    record = ls.build_profile_record(
        _register(tmp_path, MACHINERY + EXCLUDED),
        resolve=_fixed(REAL),
    )
    assert {a["celex"] for a in record["acts"]} == {"32023R1230", "32024R1689"}
    assert len(record["excluded"]) == 2
    assert all("status" not in e for e in record["excluded"])


def test_the_record_says_an_exclusion_is_a_decision_nobody_re_checks(tmp_path):
    """An exclusion can go stale — Ökodesign binds the day a delegated act appears."""
    record = ls.build_profile_record(
        _register(tmp_path, MACHINERY + EXCLUDED),
        resolve=_fixed(REAL),
    )
    assert "not monitored" in record["excluded"][0]["decided_by"]
    for lang, phrase in (
        ("en", "re-checks whether the reason still holds"),
        ("de", "prüft nach, ob ihr Grund noch trägt"),
    ):
        assert phrase in ls.render_markdown(record, lang)


def test_the_exclusions_are_shown_in_both_languages(tmp_path):
    record = ls.build_profile_record(
        _register(tmp_path, MACHINERY + EXCLUDED),
        resolve=_fixed(REAL),
    )
    english = ls.render_markdown(record, "en")
    german = ls.render_markdown(record, "de")
    assert "## What was deliberately left out" in english
    assert "## Was bewusst nicht im Register steht" in german
    assert "(32023R0988)" in german
    assert "Gehört wieder hinein, sobald:" in german


def test_a_record_without_exclusions_says_nothing_about_them(tmp_path):
    """Silence is right here: a register that excluded nothing must not imply it considered any."""
    record = ls.build_profile_record(_register(tmp_path), resolve=_fixed(REAL))
    assert record["excluded"] == []
    for lang in ls.LANGUAGES:
        rendered = ls.render_markdown(record, lang)
        assert ls.WORDS[lang]["excluded_head"] not in rendered


def test_a_pin_the_source_does_not_know_is_never_current():
    """A mistyped or invented date sorts after every real consolidation and would read as newest."""
    available = ["02024R1689-20240712", "02024R1689-20260727"]
    for pinned in ("02024R1689-20991231", "02024R1689-20240713", "02024R1689-20200101"):
        status, key, _ = ls.assess(pinned, available)
        assert (status, key) == ("unchecked", "pin_unknown"), pinned


def test_a_source_that_lists_no_consolidation_cannot_confirm_a_pin():
    """An empty answer is an answer about the source, not a confirmation of what we cite."""
    status, key, _ = ls.assess("02024R1689-20240712", [])
    assert (status, key) == ("unchecked", "pin_unknown")


def test_an_unknown_pin_says_so_in_both_languages(tmp_path):
    text = MACHINERY.replace("02023R1230-20260727", "02023R1230-20991231")
    record = ls.build_profile_record(_register(tmp_path, text), resolve=_fixed(REAL))
    by_key = {a["key"]: a for a in record["acts"]}
    assert by_key["machinery"]["status"] == "unchecked"
    assert "02023R1230-20991231" in ls.render_markdown(record, "en")
    assert "Die Quelle führt" in ls.render_markdown(record, "de")


def test_a_foreign_pin_cannot_reach_the_comparison_by_either_route(tmp_path):
    """load_profile refuses it; if one ever slipped past, assess would not call it current."""
    status, _, _ = ls.assess("02024R1689-20240712", ["02023R1230-20260727"])
    assert status == "unchecked"


# --- Two routes to the same question -----------------------------------------------------------


def _asker(answers):
    """A stand-in endpoint: maps a query fragment to an answer, or to an exception to raise."""

    def ask(query):
        for fragment, answer in answers.items():
            if fragment in query:
                if isinstance(answer, Exception):
                    raise answer
                return answer
        raise AssertionError(f"unexpected query: {query[:60]}")

    return ask


def test_the_two_routes_are_merged_not_chosen_between():
    """A route with a blind spot returns a short list, not an error. Short would read as current."""
    resolve = ls.live_resolver(
        retries=1,
        sleep=lambda _: None,
        ask=_asker(
            {
                "STRSTARTS": ["02024R1689-20240712"],
                "act_consolidated_based_on": ["02024R1689-20260727"],
            }
        ),
    )
    assert resolve("02024R1689") == ["02024R1689-20240712", "02024R1689-20260727"]


def test_one_route_still_answers_when_the_other_cannot():
    """That is the evidence we had before the second route existed; the record's wording holds."""
    resolve = ls.live_resolver(
        retries=1,
        sleep=lambda _: None,
        ask=_asker(
            {
                "STRSTARTS": ["02024R1689-20240712", "02024R1689-20260727"],
                "act_consolidated_based_on": RuntimeError("502"),
            }
        ),
    )
    assert resolve("02024R1689") == ["02024R1689-20240712", "02024R1689-20260727"]


def test_when_neither_route_answers_the_act_is_unchecked():
    """The one thing that must never become a quiet empty list."""
    resolve = ls.live_resolver(
        retries=1,
        sleep=lambda _: None,
        ask=_asker({"celex": RuntimeError("503")}),
    )
    with pytest.raises(RuntimeError, match="could not be reached"):
        resolve("02024R1689")


def test_the_relation_route_asks_about_the_act_not_the_consolidated_base():
    """0-prefixed identifiers name consolidations; the relation hangs off the act itself."""
    seen = []

    def ask(query):
        seen.append(query)
        return []

    ls.live_resolver(retries=1, sleep=lambda _: None, ask=ask)("02023R1230")
    relation = next(q for q in seen if "act_consolidated_based_on" in q)
    assert '"32023R1230"' in relation
    assert "02023R1230" not in relation


# --- Identifier rules, stated once --------------------------------------------------------------


def test_the_two_directions_are_inverses():
    """They were written out separately and could have disagreed without anything noticing."""
    for act in ("32023R1230", "32024R1689", "32014L0053", "32022R2554"):
        assert celex.act_of(celex.consolidated_base(act)) == act


def test_an_identifier_that_is_not_an_act_is_refused():
    for bad in ("62023CJ0123", "12016E/TXT", "32023R123", "02023R1230-20260727", ""):
        with pytest.raises(celex.CelexError):
            celex.consolidated_base(bad)


def test_a_pin_must_be_a_consolidation_of_its_own_act():
    celex.check_pin("02023R1230-20260727", "32023R1230", "x")
    for bad in ("02024R1689-20260727", "02023R1230", "2023R1230-20260727"):
        with pytest.raises(celex.CelexError):
            celex.check_pin(bad, "32023R1230", "x")


def test_one_unchecked_act_is_not_a_clean_run(tmp_path, monkeypatch):
    """The record says it line by line; the exit code is what a pipeline acts on."""
    from click.testing import CliRunner

    from agent_evaluator.cli import main

    text = MACHINERY.replace("    pinned: 02023R1230-20260727\n", "")
    path = _register(tmp_path, text)
    resolve = _fixed({"02023R1230": ["02023R1230-20260727"], "02024R1689": ["02024R1689-20240712"]})
    monkeypatch.setattr(ls, "live_resolver", lambda *a, **k: resolve)

    record = ls.build_profile_record(path, resolve=resolve)
    assert {a["key"]: a["status"] for a in record["acts"]} == {
        "machinery": "unchecked",
        "ai_act": "current",
    }

    result = CliRunner().invoke(main, ["legal-status", "--profile", str(path)])
    assert result.exit_code == 2, result.output
