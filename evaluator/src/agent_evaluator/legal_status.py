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
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

from .evidence import SCHEMA_VERSION as EVIDENCE_SCHEMA_VERSION
from .regulatory import load_sources

SCHEMA = (
    "https://github.com/leonkoellerwirth-arch/agentic-ai-governance-toolkit/legal-status-record"
)
SCHEMA_VERSION = "1.4.0"

Status = Literal["current", "superseded", "unchecked"]

NOT_COVERED = (
    "new legal acts not listed here",
    "national law",
    "case law",
    "supervisory guidance and interpretations",
    "technical standards",
    "delegated and implementing acts, unless listed here in their own right",
)

# The finding a reader acts on is a sentence, and a sentence exists in one language. Storing only
# the English prose would make a German record a translation of output rather than a rendering of
# a finding, so a finding carries a key and its parameters; the prose is produced from those.
# LANGUAGES must stay covered — a test fails if a key or a scope item has no German counterpart.

NOTES: dict[str, dict[str, str]] = {
    "en": {
        "no_data": (
            "No consolidation data recorded for this act. Nothing here establishes whether the "
            "cited text has been amended."
        ),
        "unreachable": (
            "The source could not be reached for this act ({error}). Nothing here establishes "
            "whether the cited text has been amended."
        ),
        "superseded": (
            "A newer consolidation exists ({newest}). Every citation against {pinned} should be "
            "re-checked before it is relied on."
        ),
        "current": (
            "No newer consolidation was found in the source at the time of the check. This says "
            "nothing about amendments not yet consolidated there."
        ),
        "base_act": (
            "The register pins the base act, so nothing here can establish whether it moved."
        ),
        "base_act_superseded": (
            "The register pins the base act while consolidations exist (newest {newest}), so "
            "nothing here can establish whether the cited text still reads as cited."
        ),
        "pin_unknown": (
            "The source does not report {pinned} among the consolidated versions of this act. A "
            "citation against a version the source does not know is not checked by this record — "
            "confirm the identifier before relying on it."
        ),
    },
    "de": {
        "no_data": (
            "Für diesen Rechtsakt liegen keine Konsolidierungsdaten vor. Nichts hier belegt, ob "
            "der zitierte Text geändert wurde."
        ),
        "unreachable": (
            "Die Quelle war für diesen Rechtsakt nicht erreichbar ({error}). Nichts hier belegt, "
            "ob der zitierte Text geändert wurde."
        ),
        "superseded": (
            "Es existiert eine neuere Konsolidierung ({newest}). Jede Fundstelle gegen {pinned} "
            "ist erneut zu prüfen, bevor man sich darauf stützt."
        ),
        "current": (
            "Zum Zeitpunkt der Prüfung meldete die Quelle keine neuere Konsolidierung. Über "
            "Änderungen, die dort noch nicht konsolidiert sind, sagt das nichts."
        ),
        "base_act": (
            "Das Register zitiert den Basisrechtsakt; damit lässt sich hier nicht feststellen, ob "
            "er sich bewegt hat."
        ),
        "base_act_superseded": (
            "Das Register zitiert den Basisrechtsakt, obwohl Konsolidierungen existieren (neueste "
            "{newest}). Damit lässt sich nicht feststellen, ob der zitierte Text noch so lautet."
        ),
        "pin_unknown": (
            "Die Quelle führt {pinned} nicht unter den konsolidierten Fassungen dieses "
            "Rechtsakts. Eine Fundstelle gegen eine Fassung, welche die Quelle nicht kennt, ist "
            "durch diesen Beleg nicht geprüft — die Kennung ist zu bestätigen, bevor man sich "
            "darauf stützt."
        ),
    },
}

NOT_COVERED_DE: dict[str, str] = {
    "new legal acts not listed here": "neue Rechtsakte, die hier nicht aufgeführt sind",
    "national law": "nationales Recht",
    "case law": "Rechtsprechung",
    "supervisory guidance and interpretations": "Aufsichtsleitlinien und Auslegungen",
    "technical standards": "technische Normen",
    "delegated and implementing acts, unless listed here in their own right": (
        "delegierte Rechtsakte und Durchführungsrechtsakte, sofern sie nicht selbst hier "
        "aufgeführt sind"
    ),
}

LANGUAGES = tuple(NOTES)


def note_text(key: str, args: dict[str, Any], lang: str = "en") -> str:
    return NOTES[lang][key].format(**args)


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
    note_key: str = ""
    note_args: dict[str, Any] = field(default_factory=dict)


def _consolidations() -> dict[str, Any]:
    from importlib.resources import files

    resource = files("agent_evaluator") / "consolidations.json"
    if not resource.is_file():
        return {}
    return json.loads(resource.read_text(encoding="utf-8"))


def assess(pinned: str | None, available: list[str]) -> tuple[Status, str, dict[str, Any]]:
    """What the source permits us to say about the pin — the only place that judgement is made.

    It takes the whole list and not just the newest entry, because the question "is the pin behind"
    presumes the source knows the pin at all. A pin the source does not list is not current and not
    superseded: it is unverified, and reporting it as either would be the record asserting a
    currency nobody checked. That case is not hypothetical — a mistyped or invented date sorts
    after every real consolidation and would otherwise read as the newest text there is.

    Comparing versions as strings is sound because they now have to be members of the same list.
    """
    newest = available[-1] if available else None
    if pinned and pinned not in available:
        return "unchecked", "pin_unknown", {"pinned": pinned, "newest": newest or "—"}
    if pinned and newest and pinned < newest:
        return "superseded", "superseded", {"newest": newest, "pinned": pinned}
    if pinned:
        return "current", "current", {}
    if newest:
        return "unchecked", "base_act_superseded", {"newest": newest}
    return "unchecked", "base_act", {}


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
                    note_text("no_data", {}),
                    note_key="no_data",
                )
            )
            continue
        available = entry.get("available") or []
        newest = available[-1] if available else None
        status, key, args = assess(pinned, available)
        out.append(
            ActStatus(
                framework.key,
                framework.act,
                framework.celex,
                pinned,
                newest,
                status,
                note_text(key, args),
                note_key=key,
                note_args=args,
            )
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
        "excluded": [],
        "source": snapshot.get("_source", "not recorded"),
        "source_id": ENDPOINT,
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
                "note_key": e.note_key,
                "note_args": e.note_args,
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
            "on_exclusions": (
                "An act recorded as deliberately excluded is the register holder's decision, "
                "taken on the date of the record. Nothing here re-checks whether the reason still "
                "holds, and an exclusion is never version-checked."
            ),
        },
    }


WORDS: dict[str, dict[str, str]] = {
    "en": {
        "title": "Legal status record",
        "prepared": "Prepared on {on}",
        "prepared_for": " for {who}",
        "source": "Source: {source}",
        "source_gloss": "every consolidated version of the listed works",
        "checked": "Source last checked: {on}",
        "not_recorded": "not recorded",
        "register": "Register: {name} ({n} acts, {file}, sha256 {digest}…)",
        "register_caveat": (
            "Why each act is in this register is stated by the register holder. This tool checks "
            "version currency; it does not verify that the selection is complete or correct."
        ),
        "table_head": "| | Act | Cited version | Newest known |",
        "base_act_cell": "— base act —",
        "unknown": "unknown",
        "meanings": "## What each entry means",
        "because": "  - In the register because: {why}",
        "watched_head": "## What was watched",
        "watched": "Watched: {watched}.",
        "not_covered": "Not covered:",
        "absence": "## What an absence of findings means",
        "excluded_head": "## What was deliberately left out",
        "excluded_line": "- **{act}**{celex} — {why_not}",
        "revisit": "  - Belongs in the register again when: {when}",
    },
    "de": {
        "title": "Rechtsstandsbeleg",
        "prepared": "Erstellt am {on}",
        "prepared_for": " für {who}",
        "source": "Quelle: {source}",
        "source_gloss": "jede konsolidierte Fassung der aufgeführten Werke",
        "checked": "Quelle zuletzt geprüft: {on}",
        "not_recorded": "nicht erfasst",
        "register": "Register: {name} ({n} Rechtsakte, {file}, sha256 {digest}…)",
        "register_caveat": (
            "Warum ein Rechtsakt in diesem Register steht, ist die Angabe des Registerführers. "
            "Dieses Werkzeug prüft die Aktualität der Fassung; es prüft nicht, ob die Auswahl "
            "vollständig oder richtig ist."
        ),
        "table_head": "| | Rechtsakt | Zitierte Fassung | Neueste bekannte |",
        "base_act_cell": "— Basisrechtsakt —",
        "unknown": "unbekannt",
        "meanings": "## Was die Einträge bedeuten",
        "because": "  - Im Register, weil: {why}",
        "watched_head": "## Was beobachtet wurde",
        "watched": "Beobachtet: {watched}.",
        "not_covered": "Nicht erfasst:",
        "absence": "## Was ein Ausbleiben von Befunden bedeutet",
        "excluded_head": "## Was bewusst nicht im Register steht",
        "excluded_line": "- **{act}**{celex} — {why_not}",
        "revisit": "  - Gehört wieder hinein, sobald: {when}",
    },
}

SCOPE_DE = {
    "watched": (
        "die konsolidierten Fassungen der{count} oben genannten Rechtsakte, und nichts sonst"
    ),
    "meaning_of_no_finding": (
        "Dass die Quelle zum oben erfassten Prüfzeitpunkt keine neuere konsolidierte Fassung der "
        "genannten Rechtsakte meldete. Es ist keine Aussage darüber, dass sich nichts Relevantes "
        "geändert hat, und keine Aussage darüber, ob eine Pflicht auf ein System zutrifft."
    ),
    "on_source_failure": (
        "Eine Prüfung, welche die Quelle nicht erreichen konnte, wird als ungeprüft erfasst, nie "
        "als aktuell."
    ),
    "on_exclusions": (
        "Ein als bewusst ausgeschlossen erfasster Rechtsakt ist eine Entscheidung des "
        "Registerführers, getroffen zum Datum des Belegs. Nichts hier prüft nach, ob ihr Grund "
        "noch trägt, und ein Ausschluss wird nie auf seine Fassung geprüft."
    ),
}


def _scope_de(record: dict[str, Any]) -> dict[str, Any]:
    """The German scope block. Rebuilt from the record, never translated out of the English."""
    register = record.get("register")
    count = f" {register['entries']}" if register else ""
    return {
        "watched": SCOPE_DE["watched"].format(count=count),
        "not_covered": [NOT_COVERED_DE[item] for item in record["scope"]["not_covered"]],
        "meaning_of_no_finding": SCOPE_DE["meaning_of_no_finding"],
        "on_source_failure": SCOPE_DE["on_source_failure"],
        "on_exclusions": SCOPE_DE["on_exclusions"],
    }


def render_markdown(record: dict[str, Any], lang: str = "en") -> str:
    """The record as prose. `lang` selects the rendering; the record itself does not change."""
    if lang not in LANGUAGES:
        raise ValueError(f"no rendering for {lang!r}; have {', '.join(LANGUAGES)}")
    w = WORDS[lang]
    mark = {"current": "✓", "superseded": "⚠", "unchecked": "—"}
    scope = _scope_de(record) if lang == "de" else record["scope"]

    prepared = w["prepared"].format(on=record["prepared_on"])
    if record["prepared_for"]:
        prepared += w["prepared_for"].format(who=record["prepared_for"])
    lines = [
        f"# {w['title']}",
        "",
        prepared + ".",
        "",
        w["source"].format(
            source=(
                f"{record['source_id']} — {w['source_gloss']}"
                if lang != "en" and record.get("source_id")
                else record["source"]
            )
        ),
        w["checked"].format(on=record["source_checked_on"] or w["not_recorded"]),
        "",
        w["table_head"],
        "|---|---|---|---|",
    ]
    register = record.get("register")
    if register:
        lines[6:6] = [
            w["register"].format(
                name=register["name"],
                n=register["entries"],
                file=register["file"],
                digest=register["sha256"][:12],
            ),
            "",
            w["register_caveat"],
        ]

    for act in record["acts"]:
        lines.append(
            f"| {mark[act['status']]} | {act['act']} ({act['celex']}) | "
            f"{act['cited_version'] or w['base_act_cell']} | "
            f"{act['newest_known_version'] or w['unknown']} |"
        )
    lines += ["", w["meanings"], ""]
    for act in record["acts"]:
        # A record written before findings carried keys still renders — in English, as it was.
        key = act.get("note_key")
        note = note_text(key, act.get("note_args") or {}, lang) if key else act["note"]
        lines.append(f"- **{act['act']}** — {note}")
        if act.get("why"):
            lines.append(w["because"].format(why=act["why"]))

    lines += [
        "",
        w["watched_head"],
        "",
        w["watched"].format(watched=scope["watched"]),
        "",
        w["not_covered"],
        "",
    ]
    lines += [f"- {item}" for item in scope["not_covered"]]
    excluded = record.get("excluded") or []
    if excluded:
        lines += ["", w["excluded_head"], ""]
        for item in excluded:
            lines.append(
                w["excluded_line"].format(
                    act=item["act"],
                    celex=f" ({item['celex']})" if item.get("celex") else "",
                    why_not=item["why_not"],
                )
            )
            if item.get("revisit_when"):
                lines.append(w["revisit"].format(when=item["revisit_when"]))

    lines += [
        "",
        w["absence"],
        "",
        scope["meaning_of_no_finding"],
        "",
        scope["on_source_failure"],
    ]
    if excluded:
        lines.append("")
        lines.append(scope["on_exclusions"])
    lines.append("")
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
class Exclusion:
    """An act deliberately left out. A register that cannot say so is a list with a gap in it."""

    act: str
    why_not: str
    celex: str | None = None
    revisit_when: str | None = None


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


def load_profile(
    path: str | Path,
) -> tuple[list[RegisterEntry], list[Exclusion], dict[str, Any]]:
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

    exclusions: list[Exclusion] = []
    for index, item in enumerate(document.get("excluded") or [], start=1):
        where = f"{file}: exclusion {index}"
        if not isinstance(item, dict):
            raise ProfileError(f"{where} is not a mapping.")
        missing = [f for f in ("act", "why_not") if not str(item.get(f) or "").strip()]
        if missing:
            raise ProfileError(f"{where} is missing {', '.join(missing)}.")
        celex = str(item.get("celex") or "").strip() or None
        if celex is not None:
            if not CELEX.fullmatch(celex):
                raise ProfileError(f"{where}: {celex!r} is not a CELEX identifier of a legal act.")
            if celex in seen_celex:
                # Watched and deliberately not watched are not both true of the same act. Rendering
                # the contradiction would leave the reader to pick which half to believe.
                raise ProfileError(f"{where}: {celex} is both listed and excluded.")
        exclusions.append(
            Exclusion(
                str(item["act"]).strip(),
                str(item["why_not"]).strip(),
                celex,
                str(item.get("revisit_when") or "").strip() or None,
            )
        )

    block = {
        "name": str(document.get("register") or file.stem),
        "file": file.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "entries": len(entries),
        "exclusions": len(exclusions),
    }
    return entries, exclusions, block


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
            args = {"error": str(error)}
            out.append(
                ActStatus(
                    entry.key,
                    entry.act,
                    entry.celex,
                    entry.pinned,
                    None,
                    "unchecked",
                    note_text("unreachable", args),
                    entry.why,
                    note_key="unreachable",
                    note_args=args,
                )
            )
            continue
        newest = available[-1] if available else None
        status, key, args = assess(entry.pinned, available)
        out.append(
            ActStatus(
                entry.key,
                entry.act,
                entry.celex,
                entry.pinned,
                newest,
                status,
                note_text(key, args),
                entry.why,
                note_key=key,
                note_args=args,
            )
        )
    return out


def build_profile_record(
    path: str | Path, prepared_for: str = "", resolve: Resolver | None = None
) -> dict[str, Any]:
    """The same record, for a register the reader supplies rather than the one we cite."""
    entries, exclusions, block = load_profile(path)
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
            "note_key": e.note_key,
            "note_args": e.note_args,
            "why": e.why,
            "why_stated_by": "the register holder; not verified by this tool",
        }
        for e in statuses_
    ]
    record["excluded"] = [
        {
            "act": e.act,
            "celex": e.celex,
            "why_not": e.why_not,
            "revisit_when": e.revisit_when,
            "decided_by": "the register holder; not verified and not monitored by this tool",
        }
        for e in exclusions
    ]
    record["scope"]["watched"] = (
        f"the consolidated versions of the {len(entries)} acts listed above, and nothing else"
    )
    return record
