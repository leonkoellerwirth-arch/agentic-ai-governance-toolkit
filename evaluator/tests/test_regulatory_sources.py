"""INV-5 — every regulatory reference is pinned to a version.

The checklists cite articles of the EU AI Act and DORA. An article number alone does not say which
version it was written against, and EU acts get amended. `regulatory_sources.yaml` pins that down;
these tests fail if a document and the source lock stop agreeing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_evaluator import celex, regulatory
from agent_evaluator.regulatory import load_sources


def test_every_cited_article_is_pinned() -> None:
    problems = regulatory.check_references()
    assert problems == [], "regulatory references and source lock disagree:\n" + "\n".join(problems)


def test_docs_match_the_source_lock() -> None:
    stale = regulatory.check_docs()
    assert stale == [], (
        "documentation has drifted from regulatory_sources.yaml: "
        + ", ".join(stale)
        + " — run `agent-eval render-docs`"
    )


def test_render_is_idempotent() -> None:
    assert regulatory.update_docs(write=False) == []


def test_scanner_reads_both_languages_and_ranges() -> None:
    found = regulatory.scan_references(
        "Art. 5 — verify. Artikel 9 — prüfen. Article 50. Art. 24–27. Annex III. Anhang IV."
    )
    assert found == {"5", "9", "50", "24-27", "annex-III", "annex-IV"}


def test_scanner_normalises_en_dash_and_hyphen_alike() -> None:
    assert regulatory.scan_references("Art. 51–55") == regulatory.scan_references("Art. 51-55")


def test_every_framework_names_the_version_it_was_checked_against() -> None:
    sources = regulatory.load_sources()
    for framework in sources.frameworks:
        assert framework.celex, f"{framework.key}: no CELEX id"
        assert framework.consolidated_as_of, f"{framework.key}: no version date"
        assert framework.url.startswith("https://eur-lex.europa.eu/"), (
            f"{framework.key}: the text must be linked at its primary source, not a summary"
        )


# The two official faces of the same text. EUR-Lex is the reading interface; the Publications
# Office Cellar repository is what it serves from, and the only one that answers a machine — the
# EUR-Lex pages return HTTP 202 with an empty body to an automated request, so a check that
# claims to have read them has read a challenge page. Anything else is commentary, and commentary
# is never a source.
OFFICIAL_SOURCES = (
    "https://eur-lex.europa.eu/",
    "http://publications.europa.eu/resource/",
    "https://publications.europa.eu/resource/",
)


def test_provenance_of_the_provenance_is_recorded() -> None:
    sources = regulatory.load_sources()
    assert sources.verification_sources
    for url in sources.verification_sources:
        assert url.startswith(OFFICIAL_SOURCES), f"not a primary source: {url}"
    assert isinstance(sources.owner_verified, bool)


def test_owner_verified_requires_a_machine_readable_source() -> None:
    """The flag may only stand on a source something could actually have read.

    It was raised on 2026-08-25 against the Cellar repository. Raising it again on the strength of
    EUR-Lex web pages alone would be raising it on a source that answers automated requests with
    an empty body.
    """
    sources = regulatory.load_sources()
    if sources.owner_verified:
        assert any(
            "publications.europa.eu/resource/" in url for url in sources.verification_sources
        ), "owner_verified is true without a source a check could have read"


# --- The shipped register holds to its own rules -------------------------------------------------


def _mutated(tmp_path, old: str, new: str):
    source = (
        Path(__file__).resolve().parents[1] / "src" / "agent_evaluator" / "regulatory_sources.yaml"
    ).read_text(encoding="utf-8")
    assert old in source, old
    path = tmp_path / "sources.yaml"
    path.write_text(source.replace(old, new, 1), encoding="utf-8")
    return path


def test_a_malformed_act_identifier_is_refused(tmp_path):
    """The consolidation check derives a base from this; a typo collects another act's versions."""
    with pytest.raises(celex.CelexError, match="not a CELEX identifier"):
        load_sources(_mutated(tmp_path, "celex: 32024R1689", "celex: 32024R168"))


def test_a_pin_belonging_to_another_act_is_refused(tmp_path):
    """The rule a supplied register has to satisfy. This register was exempt from it until now."""
    with pytest.raises(celex.CelexError, match="not a consolidation of"):
        load_sources(
            _mutated(
                tmp_path,
                "consolidated_celex: 02024R1689-20260727",
                "consolidated_celex: 02022R2554-20221227",
            )
        )


def test_an_amending_act_is_held_to_the_same_rule(tmp_path):
    with pytest.raises(celex.CelexError, match="not a CELEX identifier"):
        load_sources(_mutated(tmp_path, "celex: 32026R1744", "celex: 2026R1744"))


def test_the_shipped_register_passes_the_rules_it_imposes():
    load_sources()
