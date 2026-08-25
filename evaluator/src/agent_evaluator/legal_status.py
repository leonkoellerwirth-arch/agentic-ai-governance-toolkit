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

import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

from .evidence import SCHEMA_VERSION as EVIDENCE_SCHEMA_VERSION
from .regulatory import load_sources

SCHEMA = (
    "https://github.com/leonkoellerwirth-arch/agentic-ai-governance-toolkit/legal-status-record"
)
SCHEMA_VERSION = "1.1.0"

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
    why: str = ""


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
        "register": None,
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
    register = record.get("register")
    if register:
        lines[6:6] = [
            f"Register: {register['name']} "
            f"({register['entries']} acts, {register['file']}, sha256 {register['sha256'][:12]}…)",
            "",
            "Why each act is in this register is stated by the register holder. This tool checks "
            "version currency; it does not verify that the selection is complete or correct.",
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
        if act.get("why"):
            lines.append(f"  - In the register because: {act['why']}")

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


# --- Registers supplied by the reader --------------------------------------------------------
#
# The acts above are the ones this toolkit itself cites. A reader watching a different body of law
# — a machinery builder, a medical-device maker, a hospital — has a different register, and that
# register is theirs, not ours. `load_profile` reads it; everything downstream is unchanged.
#
# Every entry must say why the act is in the register. A register without a reason per act is a
# list, not a selection, and the selection is the part a reader is actually relying on. The reason
# is the register holder's statement. This tool does not verify it, and says so in the record.

CELEX = re.compile(r"3\d{4}[A-Z]\d{4}")
CONSOLIDATED = re.compile(r"0\d{4}[A-Z]\d{4}-\d{8}")
ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"

_QUERY = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex WHERE {
  ?w cdm:resource_legal_id_celex ?celex .
  FILTER(STRSTARTS(STR(?celex), "%s"))
} ORDER BY ?celex"""

Resolver = Callable[[str], list[str]]


class ProfileError(ValueError):
    """The register file cannot be read as a register. Never a warning — the record is not built."""


@dataclass(frozen=True)
class RegisterEntry:
    key: str
    act: str
    celex: str
    why: str
    pinned: str | None


def consolidated_base(celex: str) -> str:
    """32023R1230 -> 02023R1230. The prefix every consolidation of that work shares."""
    return "0" + celex[1:]


def load_profile(path: str | Path) -> tuple[list[RegisterEntry], dict[str, Any]]:
    """Read a register file. Returns its entries and the block that identifies it in the record."""
    import yaml

    file = Path(path)
    raw = file.read_bytes()
    try:
        document = yaml.safe_load(raw.decode("utf-8"))
    except yaml.YAMLError as error:
        raise ProfileError(f"{file}: not readable as YAML — {error}") from error
    if not isinstance(document, dict) or not isinstance(document.get("acts"), list):
        raise ProfileError(f"{file}: expected a mapping with a list under 'acts'.")

    entries: list[RegisterEntry] = []
    seen_keys: set[str] = set()
    seen_celex: set[str] = set()
    for index, item in enumerate(document["acts"], start=1):
        where = f"{file}: entry {index}"
        if not isinstance(item, dict):
            raise ProfileError(f"{where} is not a mapping.")
        missing = [f for f in ("key", "act", "celex", "why") if not str(item.get(f) or "").strip()]
        if missing:
            raise ProfileError(f"{where} is missing {', '.join(missing)}.")
        key, act = str(item["key"]).strip(), str(item["act"]).strip()
        celex, why = str(item["celex"]).strip(), str(item["why"]).strip()
        if not CELEX.fullmatch(celex):
            raise ProfileError(f"{where}: {celex!r} is not a CELEX identifier of a legal act.")
        if key in seen_keys:
            raise ProfileError(f"{where}: key {key!r} is used twice.")
        if celex in seen_celex:
            raise ProfileError(f"{where}: {celex} is listed twice.")
        seen_keys.add(key)
        seen_celex.add(celex)

        pinned = str(item.get("pinned") or "").strip() or None
        if pinned is not None:
            # Versions are compared as strings. That is only sound when both are consolidations of
            # the same work, so a pin belonging to another act is refused rather than compared.
            if not CONSOLIDATED.fullmatch(pinned):
                raise ProfileError(
                    f"{where}: {pinned!r} is not a consolidated CELEX (0YYYYTNNNN-YYYYMMDD)."
                )
            if not pinned.startswith(consolidated_base(celex) + "-"):
                raise ProfileError(
                    f"{where}: pinned {pinned} is not a consolidation of {celex}. Comparing them "
                    "would report a currency that was never checked."
                )
        entries.append(RegisterEntry(key, act, celex, why, pinned))

    if not entries:
        raise ProfileError(f"{file}: the register lists no acts.")

    block = {
        "name": str(document.get("register") or file.stem),
        "file": file.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "entries": len(entries),
    }
    return entries, block


def live_resolver(retries: int = 4, backoff: float = 4.0, sleep=time.sleep) -> Resolver:
    """Ask the Publications Office which consolidations of a work exist.

    The endpoint answers 502/503 under load often enough that a single attempt is not a check.
    Retries; if it still cannot be reached, it raises — and the caller records the act as
    unchecked. It is never reported as current on the strength of an answer that never arrived.
    """

    def resolve(base: str) -> list[str]:
        last: Exception | None = None
        for attempt in range(retries):
            try:
                query = urllib.parse.urlencode({"format": "application/sparql-results+json"})
                body = urllib.parse.urlencode({"query": _QUERY % base}).encode()
                request = urllib.request.Request(
                    f"{ENDPOINT}?{query}",
                    data=body,
                    headers={"Accept": "application/sparql-results+json"},
                )
                with urllib.request.urlopen(request, timeout=120) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                return sorted(row["celex"]["value"] for row in payload["results"]["bindings"])
            except Exception as error:  # network, endpoint, malformed answer
                last = error
                if attempt < retries - 1:
                    sleep(backoff * (attempt + 1))
        raise RuntimeError(f"{ENDPOINT} could not be reached for {base}: {last}")

    return resolve


def profile_statuses(entries: list[RegisterEntry], resolve: Resolver) -> list[ActStatus]:
    out: list[ActStatus] = []
    for entry in entries:
        try:
            available = resolve(consolidated_base(entry.celex))
        except Exception as error:
            out.append(
                ActStatus(
                    entry.key,
                    entry.act,
                    entry.celex,
                    entry.pinned,
                    None,
                    "unchecked",
                    f"The source could not be reached for this act ({error}). Nothing here "
                    "establishes whether the cited text has been amended.",
                    entry.why,
                )
            )
            continue
        newest = available[-1] if available else None
        if entry.pinned and newest and entry.pinned < newest:
            status: Status = "superseded"
            note = (
                f"A newer consolidation exists ({newest}). Every citation against {entry.pinned} "
                "should be re-checked before it is relied on."
            )
        elif entry.pinned:
            status = "current"
            note = (
                "No newer consolidation was found in the source at the time of the check. "
                "This says nothing about amendments not yet consolidated there."
            )
        elif newest:
            status = "unchecked"
            note = (
                f"The register pins the base act while consolidations exist (newest {newest}), so "
                "nothing here can establish whether the cited text still reads as cited."
            )
        else:
            status = "unchecked"
            note = "The register pins the base act, so nothing here can establish whether it moved."
        out.append(
            ActStatus(
                entry.key, entry.act, entry.celex, entry.pinned, newest, status, note, entry.why
            )
        )
    return out


def build_profile_record(
    path: str | Path, prepared_for: str = "", resolve: Resolver | None = None
) -> dict[str, Any]:
    """The same record, for a register the reader supplies rather than the one we cite."""
    entries, block = load_profile(path)
    statuses_ = profile_statuses(entries, resolve or live_resolver())
    record = build_record(prepared_for)
    record["register"] = block
    record["source"] = f"SPARQL, {ENDPOINT} — every consolidated version of the listed works"
    record["source_checked_on"] = date.today().isoformat()
    record["acts"] = [
        {
            "key": e.key,
            "act": e.act,
            "celex": e.celex,
            "cited_version": e.pinned,
            "newest_known_version": e.newest_known,
            "status": e.status,
            "note": e.note,
            "why": e.why,
            "why_stated_by": "the register holder; not verified by this tool",
        }
        for e in statuses_
    ]
    record["scope"]["watched"] = (
        f"the consolidated versions of the {len(entries)} acts listed above, and nothing else"
    )
    return record
