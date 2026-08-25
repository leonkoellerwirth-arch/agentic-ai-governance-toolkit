"""Conformance: the published schema, and every manifest this tool writes.

A published schema nobody checks is documentation. These tests are the check — the schema is
itself valid, the manifests this tool produces satisfy it, and the malformed shapes a second
implementation would plausibly emit are rejected rather than tolerated.

That is the difference between "our output happens to look like this" and a format another tool
can target.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from agent_evaluator import evidence as ev

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "08-evidence" / "evidence-manifest.schema.json"
)


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def manifest(tmp_path: Path) -> dict[str, Any]:
    (tmp_path / "readiness.json").write_text('{"gaps": []}', encoding="utf-8")
    (tmp_path / "summary.md").write_text("# summary\n", encoding="utf-8")
    return ev.build_manifest(tmp_path, commit="abc1234")


def test_the_published_schema_is_itself_valid(schema: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(schema)


def test_the_schema_declares_the_version_the_tool_writes(schema: dict[str, Any]) -> None:
    """The $id pins a version; drifting from what the tool emits would publish a lie."""
    assert schema["$id"].endswith(f"/{ev.SCHEMA_VERSION}")


def test_a_manifest_this_tool_writes_conforms(
    schema: dict[str, Any], manifest: dict[str, Any]
) -> None:
    Draft202012Validator(schema).validate(manifest)


def test_a_manifest_without_a_commit_conforms(schema: dict[str, Any], tmp_path: Path) -> None:
    """Running outside a checkout is legitimate; the field goes null, it does not vanish."""
    (tmp_path / "readiness.json").write_text("{}", encoding="utf-8")
    Draft202012Validator(schema).validate(ev.build_manifest(tmp_path, commit=""))


@pytest.mark.parametrize(
    ("mutate", "why"),
    [
        (lambda m: m.pop("ruleset"), "a manifest without a ruleset fingerprint proves nothing"),
        (lambda m: m.pop("tool"), "an artifact that cannot name its producer is not evidence"),
        (
            lambda m: m.__setitem__("schema_version", "1.0"),
            "a two-part version cannot express a compatible change",
        ),
        (
            lambda m: m["artifacts"][0].__setitem__("digest", "deadbeef"),
            "a digest without its algorithm cannot be re-checked",
        ),
        (
            lambda m: m["ruleset"].__setitem__("files", {}),
            "an empty fingerprint records that rules existed, not which",
        ),
        (
            lambda m: m.__setitem__("extra", "smuggled"),
            "an unknown top-level field would let a producer add meaning consumers cannot see",
        ),
        (
            lambda m: m["artifacts"][0].__setitem__("bytes", -1),
            "a negative length is a producer bug, not a permitted value",
        ),
    ],
)
def test_malformed_manifests_are_rejected(
    schema: dict[str, Any], manifest: dict[str, Any], mutate, why: str
) -> None:
    broken = copy.deepcopy(manifest)
    mutate(broken)
    assert list(Draft202012Validator(schema).iter_errors(broken)), why
