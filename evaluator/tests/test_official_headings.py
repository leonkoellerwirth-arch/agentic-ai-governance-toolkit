"""The register against the primary text.

`official_headings.json` holds the heading of every article this toolkit cites, taken from the
Publications Office Cellar repository — the official machine interface to the same text EUR-Lex
renders. These tests compare the register against it, so "verified" is a property the build
re-establishes rather than a claim about one afternoon.

Refreshing the snapshot needs the network and is therefore a script, not a test: the gate stays
offline. What the gate does check is that the register and the committed snapshot agree.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

PKG = Path(__file__).resolve().parents[1] / "src" / "agent_evaluator"
SNAPSHOT = PKG / "official_headings.json"
REGISTER = PKG / "regulatory_sources.yaml"

# Words that carry no distinguishing meaning, plus the scope hint this register appends to
# high-risk topics and the primary text does not.
_FILLER = {"and", "of", "the", "for", "on", "in", "to", "a", "an", "or", "as", "high-risk"}


def _tokens(text: str) -> set[str]:
    words = re.sub(r"[^\w\s-]", " ", text.lower()).split()
    return {w for w in words if w not in _FILLER}


@pytest.fixture(scope="module")
def snapshot() -> dict:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def register() -> dict:
    return yaml.safe_load(REGISTER.read_text(encoding="utf-8"))


def _official(snapshot: dict, framework: str, ref_id: str) -> str:
    """The official heading, or the joined headings of a range like 51-55."""
    headings = snapshot["frameworks"][framework]["headings"]
    if ref_id in headings:
        return headings[ref_id]
    if "-" in ref_id and not ref_id.startswith("annex"):
        low, high = ref_id.split("-", 1)
        return " ".join(headings.get(str(n), "") for n in range(int(low), int(high) + 1))
    return ""


def test_every_reference_has_an_official_heading(snapshot: dict, register: dict) -> None:
    """A reference the snapshot cannot resolve is a reference nothing checks."""
    for framework in register["frameworks"]:
        for ref in framework["references"]:
            official = _official(snapshot, framework["key"], str(ref["id"]))
            assert official, f"{framework['key']} {ref['id']}: no official heading in the snapshot"


def test_no_topic_says_something_the_official_heading_does_not(
    snapshot: dict, register: dict
) -> None:
    """The failure this exists for.

    A topic may abbreviate the heading — "record-keeping" for "Record-keeping" — but it may not
    introduce a word the heading does not carry. That is how Article 13 came to be labelled
    "instructions for use" when the article is about transparency and information to deployers:
    the label described one obligation inside it and pointed the reader at the wrong thing.
    """
    problems = []
    for framework in register["frameworks"]:
        for ref in framework["references"]:
            official = _official(snapshot, framework["key"], str(ref["id"]))
            allowed = (
                snapshot.get("context_allowed", {})
                .get(framework["key"], {})
                .get(str(ref["id"]), {})
            )
            extra = _tokens(ref["topic"]) - _tokens(official) - set(allowed.get("terms", []))
            if extra:
                problems.append(
                    f"  {framework['key']} {ref['id']}: topic adds {sorted(extra)} — "
                    f"official heading is {official!r}"
                )
    assert not problems, "topics claiming more than the primary text says:\n" + "\n".join(problems)


def test_every_declared_context_addition_carries_a_reason(snapshot: dict) -> None:
    """The allow-list is where a wrong label would hide, so each entry has to argue for itself."""
    for framework, refs in snapshot.get("context_allowed", {}).items():
        for ref_id, entry in refs.items():
            assert entry.get("terms"), f"{framework} {ref_id}: declared with no terms"
            assert len(str(entry.get("reason", "")).split()) >= 8, (
                f"{framework} {ref_id}: a declared exception needs a reason, not a note"
            )


def test_no_declared_exception_is_stale(snapshot: dict, register: dict) -> None:
    """An exception that is no longer needed must go, or the list becomes decoration."""
    stale = []
    for framework in register["frameworks"]:
        refs = snapshot.get("context_allowed", {}).get(framework["key"], {})
        for ref in framework["references"]:
            entry = refs.get(str(ref["id"]))
            if not entry:
                continue
            official = _official(snapshot, framework["key"], str(ref["id"]))
            if not (_tokens(ref["topic"]) - _tokens(official)):
                stale.append(f"  {framework['key']} {ref['id']}: no longer adds anything")
    assert not stale, "declared exceptions that are no longer needed:\n" + "\n".join(stale)


def test_the_snapshot_names_where_it_came_from(snapshot: dict) -> None:
    assert "publications.europa.eu" in snapshot["_source"]
    assert snapshot["_fetched"]
    for framework in snapshot["frameworks"].values():
        assert framework["celex"]
        assert framework["uri"].startswith("http")


def test_owner_verified_implies_a_method_that_names_the_primary_source(register: dict) -> None:
    """The flag may only stand while the method says how, and against what."""
    verification = register["verification"]
    if verification.get("owner_verified"):
        assert "publications.europa.eu" in verification["method"], (
            "owner_verified is true but the method does not name the primary source it was "
            "checked against"
        )
        assert verification["verified_at"]
