"""INV-5 — every regulatory reference is pinned to a version.

The checklists cite articles of the EU AI Act and DORA. An article number alone does not say which
version it was written against, and EU acts get amended. `regulatory_sources.yaml` pins that down;
these tests fail if a document and the source lock stop agreeing.
"""

from __future__ import annotations

from agent_evaluator import regulatory


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


def test_provenance_of_the_provenance_is_recorded() -> None:
    # Commentary is never a source. If the recorded sources are not EUR-Lex, the lock is worthless.
    sources = regulatory.load_sources()
    assert sources.verification_sources
    for url in sources.verification_sources:
        assert url.startswith("https://eur-lex.europa.eu/"), f"not a primary source: {url}"
    assert isinstance(sources.owner_verified, bool)
