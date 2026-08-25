"""Tests for the evidence manifest.

The manifest is the difference between a directory of results and a set an auditor can archive.
These check the properties that difference rests on: it names the tool and the rulesets by digest,
it covers every file the run wrote, and a byte changed after the fact no longer matches.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_evaluator import __version__
from agent_evaluator import evidence as ev


@pytest.fixture
def evidence_dir(tmp_path: Path) -> Path:
    (tmp_path / "readiness.json").write_text('{"gaps": []}', encoding="utf-8")
    (tmp_path / "summary.md").write_text("# summary\n", encoding="utf-8")
    return tmp_path


def test_manifest_names_the_tool_and_its_version(evidence_dir: Path) -> None:
    manifest = ev.build_manifest(evidence_dir)
    assert manifest["tool"] == {"name": "agent-eval", "version": __version__}


def test_manifest_is_versioned_separately_from_the_tool(evidence_dir: Path) -> None:
    """A consumer targets schema_version; the tool may move underneath it."""
    manifest = ev.build_manifest(evidence_dir)
    assert manifest["schema_version"] != __version__
    assert manifest["schema"].startswith("https://")


def test_manifest_fingerprints_the_rulesets_that_decided_the_outcome() -> None:
    fingerprint = ev.ruleset_fingerprint()
    for name in ev.RULESET_FILES:
        assert name in fingerprint["files"], f"{name} is not fingerprinted"
        assert fingerprint["files"][name].startswith("sha256:")
    assert fingerprint["digest"].startswith("sha256:")


def test_a_changed_ruleset_changes_the_fingerprint(monkeypatch: pytest.MonkeyPatch) -> None:
    """Otherwise the fingerprint records a version number, not the rules in force."""
    before = ev.ruleset_fingerprint()["digest"]
    monkeypatch.setattr(ev, "RULESET_FILES", ev.RULESET_FILES[:-1])
    assert ev.ruleset_fingerprint()["digest"] != before


def test_manifest_covers_every_artifact(evidence_dir: Path) -> None:
    names = {a["file"] for a in ev.build_manifest(evidence_dir)["artifacts"]}
    assert names == {"readiness.json", "summary.md"}


def test_manifest_does_not_cover_itself(evidence_dir: Path) -> None:
    ev.write_manifest(evidence_dir)
    names = {a["file"] for a in ev.build_manifest(evidence_dir)["artifacts"]}
    assert ev.MANIFEST_NAME not in names


def test_editing_an_artifact_breaks_its_digest(evidence_dir: Path) -> None:
    """The one property the manifest actually proves."""
    manifest = json.loads(ev.write_manifest(evidence_dir).read_text(encoding="utf-8"))
    recorded = {a["file"]: a["digest"] for a in manifest["artifacts"]}
    (evidence_dir / "readiness.json").write_text('{"gaps": ["quietly removed"]}', encoding="utf-8")
    now = {a["file"]: a["digest"] for a in ev.build_manifest(evidence_dir)["artifacts"]}
    assert now["readiness.json"] != recorded["readiness.json"]
    assert now["summary.md"] == recorded["summary.md"]


def test_manifest_says_what_it_does_not_prove(evidence_dir: Path) -> None:
    """A digest shows the set is unedited. It shows nothing about authorisation."""
    note = ev.build_manifest(evidence_dir)["note"]
    assert "not show" in note or "do not show" in note
