"""INV-1 — the rubric exists exactly once.

The documentation tables in docs/02-risk-assessment/ are generated from rubric.yaml. If anyone edits
one without the other, this test fails and names the file to regenerate.
"""

from __future__ import annotations

from agent_evaluator import rubric


def test_docs_match_the_single_source() -> None:
    stale = rubric.check_docs()
    assert stale == [], (
        "documentation has drifted from rubric.yaml: "
        + ", ".join(stale)
        + " — run `agent-eval render-docs`"
    )


def test_every_dimension_and_band_is_rendered() -> None:
    r = rubric.load_rubric()
    dimensions_md = rubric.render_block("dimensions", r)
    for dim in r.dimensions:
        assert dim.label in dimensions_md
    bands_md = rubric.render_block("bands", r)
    for band in r.bands:
        assert band.level in bands_md and band.name in bands_md


def test_render_is_idempotent() -> None:
    # Rendering already-current docs must report no changes.
    assert rubric.update_docs(write=False) == []
