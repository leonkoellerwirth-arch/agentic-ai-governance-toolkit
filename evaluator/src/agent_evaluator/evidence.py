"""The evidence manifest — what makes a gate run archivable rather than merely produced.

A check writes its result as JSON. That file says what was found and nothing about where it came
from: not which tool, not which ruleset, not when, not against which commit. An auditor receiving
it a year later cannot answer the first question they will be asked.

The manifest answers it, next to the results rather than inside them, so no existing consumer of
``agent-eval <command> --json`` breaks. It records the tool and its version, a fingerprint of the
rulesets that were in force, the commit under test, the time, and a SHA-256 of every evidence file
— which is what turns a directory of JSON into a set an auditor can verify has not been edited
since.

The format is versioned separately from the tool on purpose. A consumer targets
``schema_version``; the tool may move underneath it.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from typing import Any

from . import __version__

SCHEMA = "https://github.com/leonkoellerwirth-arch/agentic-ai-governance-toolkit/evidence-manifest"
SCHEMA_VERSION = "1.0.0"
MANIFEST_NAME = "manifest.json"

# The rulesets whose content decides an outcome. Fingerprinting them is what lets a reader say
# "this run used these rules", rather than trusting that the version number implies it.
RULESET_FILES: tuple[str, ...] = (
    "rubric.yaml",
    "readiness.yaml",
    "action_authority.yaml",
    "policy_decisions.yaml",
    "regulatory_sources.yaml",
)


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def ruleset_fingerprint() -> dict[str, Any]:
    """A per-file digest plus one digest over all of them, in a fixed order."""
    per_file: dict[str, str] = {}
    combined = hashlib.sha256()
    for name in RULESET_FILES:
        resource = files("agent_evaluator") / name
        if not resource.is_file():
            continue
        raw = resource.read_bytes()
        per_file[name] = _sha256(raw)
        combined.update(raw)
    return {"files": per_file, "digest": "sha256:" + combined.hexdigest()}


def build_manifest(
    evidence_dir: Path,
    *,
    commit: str = "",
    produced_at: str | None = None,
) -> dict[str, Any]:
    """Describe every evidence file in the directory, with its digest."""
    artifacts = []
    for path in sorted(evidence_dir.iterdir()):
        if not path.is_file() or path.name == MANIFEST_NAME:
            continue
        raw = path.read_bytes()
        artifacts.append(
            {
                "file": path.name,
                "bytes": len(raw),
                "digest": _sha256(raw),
            }
        )

    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "produced_at": produced_at or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "tool": {"name": "agent-eval", "version": __version__},
        "ruleset": ruleset_fingerprint(),
        "commit": commit or None,
        "artifacts": artifacts,
        "note": (
            "Digests cover the files as written by this run. They show that the set has not been "
            "edited since; they do not show that a check was authorised, complete or correct."
        ),
    }


def write_manifest(evidence_dir: Path, *, commit: str = "") -> Path:
    manifest = build_manifest(evidence_dir, commit=commit)
    target = evidence_dir / MANIFEST_NAME
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return target
