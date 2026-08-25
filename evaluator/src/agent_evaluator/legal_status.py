"""The legal-status record — what a reader is entitled to conclude, and what they are not.

A control mapping cites a legal text. Months later the question is not what the mapping says but
whether the text still says it. This produces the answer as an artifact: for every act the register
pins, the version cited, the newest version the Publications Office reports, when that was checked,
and against which source.

**The scope statement is part of the record, not a footnote.** A monthly report that says nothing
is read as "nothing changed", and that reading is only defensible if the record states precisely
what was watched and what was not. A record that cannot say what it did not look at is a promise of
completeness nobody can keep.

A check that could not reach the source is reported as a disruption, never as "current". That is
the single failure mode that turns this kind of record from evidence into false comfort.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

from .evidence import SCHEMA_VERSION as EVIDENCE_SCHEMA_VERSION
from .regulatory import load_sources

SCHEMA = (
    "https://github.com/leonkoellerwirth-arch/agentic-ai-governance-toolkit/legal-status-record"
)
SCHEMA_VERSION = "1.0.0"

Status = Literal["current", "superseded", "unchecked"]

NOT_COVERED = (
    "new legal acts not listed here",
    "national law",
    "case law",
    "supervisory guidance and interpretations",
    "technical standards",
    "delegated and implementing acts, unless listed here in their own right",
)


@dataclass(frozen=True)
class ActStatus:
    key: str
    act: str
    celex: str
    pinned: str | None
    newest_known: str | None
    status: Status
    note: str


def _consolidations() -> dict[str, Any]:
    from importlib.resources import files

    resource = files("agent_evaluator") / "consolidations.json"
    if not resource.is_file():
        return {}
    return json.loads(resource.read_text(encoding="utf-8"))


def statuses() -> tuple[list[ActStatus], str | None]:
    """One entry per pinned act, plus the date the consolidation data was last obtained."""
    sources = load_sources()
    snapshot = _consolidations()
    checked = snapshot.get("_checked")
    frameworks = snapshot.get("frameworks", {})

    out: list[ActStatus] = []
    for framework in sources.frameworks:
        entry = frameworks.get(framework.key)
        pinned = framework.consolidated_celex or None
        if entry is None:
            out.append(
                ActStatus(
                    framework.key,
                    framework.act,
                    framework.celex,
                    pinned,
                    None,
                    "unchecked",
                    "No consolidation data recorded for this act. Nothing here establishes whether "
                    "the cited text has been amended.",
                )
            )
            continue
        available = entry.get("available") or []
        newest = available[-1] if available else None
        if pinned and newest and pinned < newest:
            note = (
                f"A newer consolidation exists ({newest}). Every citation against {pinned} should "
                "be re-checked before it is relied on."
            )
            status: Status = "superseded"
        elif pinned:
            note = (
                "No newer consolidation was found in the source at the time of the check. "
                "This says nothing about amendments not yet consolidated there."
            )
            status = "current"
        else:
            note = "The register pins the base act, so nothing here can establish whether it moved."
            status = "unchecked"
        out.append(
            ActStatus(framework.key, framework.act, framework.celex, pinned, newest, status, note)
        )
    return out, checked


def build_record(prepared_for: str = "") -> dict[str, Any]:
    entries, checked = statuses()
    snapshot = _consolidations()
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "prepared_on": date.today().isoformat(),
        "prepared_for": prepared_for or None,
        "source": snapshot.get("_source", "not recorded"),
        "source_checked_on": checked,
        "acts": [
            {
                "key": e.key,
                "act": e.act,
                "celex": e.celex,
                "cited_version": e.pinned,
                "newest_known_version": e.newest_known,
                "status": e.status,
                "note": e.note,
            }
            for e in entries
        ],
        "scope": {
            "watched": "the consolidated versions of the acts listed above, and nothing else",
            "not_covered": list(NOT_COVERED),
            "meaning_of_no_finding": (
                "That at the check recorded above, the source reported no newer consolidated "
                "version of the listed acts. It is not a statement that nothing relevant changed, "
                "and not a statement that an obligation does or does not apply to any system."
            ),
            "on_source_failure": (
                "A check that could not reach the source is recorded as unchecked, never as "
                "current."
            ),
        },
    }


def render_markdown(record: dict[str, Any]) -> str:
    mark = {"current": "✓", "superseded": "⚠", "unchecked": "—"}
    lines = [
        "# Legal status record",
        "",
        f"Prepared on {record['prepared_on']}"
        + (f" for {record['prepared_for']}" if record["prepared_for"] else "")
        + ".",
        "",
        f"Source: {record['source']}",
        f"Source last checked: {record['source_checked_on'] or 'not recorded'}",
        "",
        "| | Act | Cited version | Newest known | ",
        "|---|---|---|---|",
    ]
    for act in record["acts"]:
        lines.append(
            f"| {mark[act['status']]} | {act['act']} ({act['celex']}) | "
            f"{act['cited_version'] or '— base act —'} | "
            f"{act['newest_known_version'] or 'unknown'} |"
        )
    lines += ["", "## What each entry means", ""]
    for act in record["acts"]:
        lines.append(f"- **{act['act']}** — {act['note']}")

    scope = record["scope"]
    lines += [
        "",
        "## What was watched",
        "",
        f"Watched: {scope['watched']}.",
        "",
        "Not covered:",
        "",
    ]
    lines += [f"- {item}" for item in scope["not_covered"]]
    lines += [
        "",
        "## What an absence of findings means",
        "",
        scope["meaning_of_no_finding"],
        "",
        scope["on_source_failure"],
        "",
    ]
    return "\n".join(lines)
