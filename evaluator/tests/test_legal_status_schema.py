"""Conformance: the published schema, and every record this tool writes.

The record carries a `schema` field naming a document. Until this file existed the field named
nothing — a consumer following the identifier found a 404, which is the same class of overclaim the
record itself exists to avoid. These tests are what turns the identifier into a promise: the schema
is valid, every shape the tool emits satisfies it, and the shapes that would make the record
dishonest are rejected rather than tolerated.

The strictest of them is the last group. A record without its scope block, or with an empty
not-covered list, would assert a completeness nobody can keep. The schema refuses it, so a second
implementation of this format cannot quietly drop the part that makes an empty finding readable.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, ValidationError

from agent_evaluator import legal_status as ls

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "08-evidence" / "legal-status-record.schema.json"
)

REGISTER = """
register: Conformance register
acts:
  - key: machinery
    act: Machinery Regulation
    celex: 32023R1230
    pinned: 02023R1230-20260727
    why: The products placed on the market are machinery.
excluded:
  - act: ATEX Directive 2014/34/EU
    celex: 32014L0034
    why_not: Only for equipment in explosive atmospheres.
    revisit_when: A product is intended for such an atmosphere.
"""


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator(schema: dict[str, Any]) -> Draft202012Validator:
    return Draft202012Validator(schema)


@pytest.fixture
def record(tmp_path: Path) -> dict[str, Any]:
    path = tmp_path / "register.yaml"
    path.write_text(REGISTER, encoding="utf-8")
    return ls.build_profile_record(path, "Beispiel GmbH", resolve=lambda base: [f"{base}-20260727"])


def test_the_published_schema_is_itself_valid(schema: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(schema)


def test_the_schema_declares_the_version_the_tool_writes(schema: dict[str, Any]) -> None:
    """The $id pins a version; drifting from what the tool emits would publish a lie."""
    assert schema["$id"] == f"{ls.SCHEMA}/{ls.SCHEMA_VERSION}"


def test_the_schema_knows_every_finding_the_tool_can_produce(schema: dict[str, Any]) -> None:
    """Otherwise a new finding would fail validation on the day it first mattered."""
    declared = set(schema["$defs"]["act"]["properties"]["note_key"]["enum"])
    assert declared == set(ls.NOTES["en"])


def test_the_record_this_tool_ships_conforms(validator: Draft202012Validator) -> None:
    validator.validate(ls.build_record("Beispiel GmbH"))


def test_a_record_against_a_supplied_register_conforms(
    validator: Draft202012Validator, record: dict[str, Any]
) -> None:
    validator.validate(record)


def test_a_record_with_nothing_prepared_for_conforms(validator: Draft202012Validator) -> None:
    """Running without a client is legitimate; the field goes null, it does not vanish."""
    validator.validate(ls.build_record())


def test_a_record_of_unreachable_acts_conforms(
    validator: Draft202012Validator, tmp_path: Path
) -> None:
    """The failure case has to be expressible in the format, or it will not be reported in it."""
    path = tmp_path / "register.yaml"
    path.write_text(REGISTER, encoding="utf-8")

    def unreachable(_base: str) -> list[str]:
        raise RuntimeError("503")

    record = ls.build_profile_record(path, resolve=unreachable)
    assert record["acts"][0]["status"] == "unchecked"
    validator.validate(record)


# --- The shapes that would make the record dishonest --------------------------------------------


def test_a_record_without_its_scope_is_refused(
    validator: Draft202012Validator, record: dict[str, Any]
) -> None:
    """A record that cannot say what it did not look at promises a completeness nobody can keep."""
    broken = copy.deepcopy(record)
    del broken["scope"]
    with pytest.raises(ValidationError):
        validator.validate(broken)


def test_a_scope_that_excludes_nothing_is_refused(
    validator: Draft202012Validator, record: dict[str, Any]
) -> None:
    broken = copy.deepcopy(record)
    broken["scope"]["not_covered"] = []
    with pytest.raises(ValidationError):
        validator.validate(broken)


def test_a_status_outside_the_three_is_refused(
    validator: Draft202012Validator, record: dict[str, Any]
) -> None:
    """ "probably current" is the shape a second implementation would reach for first."""
    broken = copy.deepcopy(record)
    broken["acts"][0]["status"] = "probably current"
    with pytest.raises(ValidationError):
        validator.validate(broken)


def test_a_cited_version_that_is_not_a_consolidation_is_refused(
    validator: Draft202012Validator, record: dict[str, Any]
) -> None:
    broken = copy.deepcopy(record)
    broken["acts"][0]["cited_version"] = "32023R1230"
    with pytest.raises(ValidationError):
        validator.validate(broken)


def test_an_exclusion_without_a_reason_is_refused(
    validator: Draft202012Validator, record: dict[str, Any]
) -> None:
    broken = copy.deepcopy(record)
    del broken["excluded"][0]["why_not"]
    with pytest.raises(ValidationError):
        validator.validate(broken)


def test_an_exclusion_carrying_a_status_is_refused(
    validator: Draft202012Validator, record: dict[str, Any]
) -> None:
    """An exclusion is never version-checked. A status on one would say it was."""
    broken = copy.deepcopy(record)
    broken["excluded"][0]["status"] = "current"
    with pytest.raises(ValidationError):
        validator.validate(broken)
