"""Is the pin still the newest consolidation?

A pin makes a citation checkable and never notices that the law moved.
`scripts/check-consolidations.sh` asks the Publications Office which consolidations exist; this
compares the register against what that answer was when it was recorded, and stays offline.

The failure it exists for is silence: a register that keeps citing a superseded text says nothing
about it, and every control mapping built on that citation ages with it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

PKG = Path(__file__).resolve().parents[1] / "src" / "agent_evaluator"
SNAPSHOT = PKG / "consolidations.json"
REGISTER = PKG / "regulatory_sources.yaml"


@pytest.fixture(scope="module")
def snapshot() -> dict:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def register() -> dict:
    return yaml.safe_load(REGISTER.read_text(encoding="utf-8"))


def test_every_framework_pins_a_consolidation(register: dict) -> None:
    """Pinning the base act leaves the register unable to say whether the text has moved."""
    for framework in register["frameworks"]:
        assert framework.get("consolidated_celex"), (
            f"{framework['key']}: pins the base act, so nothing here can notice an amendment"
        )


def test_the_pin_is_the_newest_consolidation_recorded(snapshot: dict, register: dict) -> None:
    behind = []
    for framework in register["frameworks"]:
        entry = snapshot["frameworks"].get(framework["key"])
        assert entry, f"{framework['key']}: not covered by the consolidation check"
        available = entry["available"]
        pinned = str(framework["consolidated_celex"])
        if available and pinned < available[-1]:
            behind.append(
                f"  {framework['key']}: pinned {pinned}, newest recorded {available[-1]} — "
                "run scripts/check-consolidations.sh and move the pin"
            )
    assert not behind, "the register cites a superseded text:\n" + "\n".join(behind)


def test_the_snapshot_says_when_it_was_checked(snapshot: dict) -> None:
    """Without a date, "no newer version" is a claim with no shelf life."""
    assert snapshot["_checked"]
    assert "sparql" in snapshot["_source"].lower()
