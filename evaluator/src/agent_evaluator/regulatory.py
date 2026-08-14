"""Load, model, and render the regulatory source lock.

``regulatory_sources.yaml`` (shipped as package data) is the single source of truth for every
regulatory reference the checklists make. This module reads it, renders the source-lock block at
the head of each checklist and the full table in ``docs/03-checklists/regulatory-sources.md``, and
checks that documents and registry agree in both directions:

- a checklist citing an article the registry does not carry is an unpinned reference;
- a registry entry no checklist cites is a leftover, and leftovers rot quietly.

- ``python -m agent_evaluator.regulatory --write``  regenerates the doc blocks from the YAML.
- ``python -m agent_evaluator.regulatory --check``  exits non-zero if anything is stale or unpinned.

The consistency test (``tests/test_regulatory_sources.py``) calls :func:`check_docs` and
:func:`check_references`.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import yaml

# "Art. 5", "Art. 24–27", "Artikel 9", "Article 50", "Annex III", "Anhang IV".
# En dash and hyphen both occur in the docs; both normalise to a hyphen.
_REFERENCE = re.compile(
    r"\b(?:Art\.|Artikel|Article)\s?(?P<article>\d+(?:\s*[–-]\s*\d+)?)"
    r"|\b(?:Annex|Anhang)\s(?P<annex>[IVX]+)\b"
)


@dataclass(frozen=True)
class Reference:
    id: str
    topic: str


def _oj_de(citation: str) -> str:
    """German cites the Official Journal as "ABl." with "S." for pages; numbering stays verbatim."""
    return citation.replace("OJ ", "ABl. ", 1).replace("pp. ", "S. ", 1)


@dataclass(frozen=True)
class Amendment:
    act: str
    act_de: str
    celex: str
    oj: str
    in_force: str
    note: str


@dataclass(frozen=True)
class Framework:
    key: str
    label: str
    act: str
    act_de: str
    celex: str
    oj: str
    consolidated_as_of: str
    url: str
    consolidated_celex: str | None
    amended_by: tuple[Amendment, ...]
    references: tuple[Reference, ...]

    @property
    def reference_ids(self) -> frozenset[str]:
        return frozenset(r.id for r in self.references)

    def version_line(self, lang: str = "en") -> str:
        """How to name the exact text these references point at."""
        if lang == "de":
            if self.consolidated_celex:
                return f"konsolidierte Fassung {self.consolidated_celex}, Stand {self.consolidated_as_of}"  # noqa: E501
            return f"Stand {self.consolidated_as_of}"
        if self.consolidated_celex:
            return f"consolidated text {self.consolidated_celex}, as of {self.consolidated_as_of}"
        return f"as of {self.consolidated_as_of}"


@dataclass(frozen=True)
class Sources:
    version: int
    title: str
    frameworks: tuple[Framework, ...]
    documents: tuple[tuple[str, str, str], ...]  # (repo-relative path, framework key, language)
    verified_at: str
    verification_method: str
    verification_sources: tuple[str, ...]
    owner_verified: bool

    def framework(self, key: str) -> Framework:
        for fw in self.frameworks:
            if fw.key == key:
                return fw
        raise KeyError(f"no framework {key!r} in the source lock")


def load_sources(path: str | Path | None = None) -> Sources:
    """Load the source lock from ``path`` (defaults to the packaged YAML)."""
    if path is None:
        raw = (files("agent_evaluator") / "regulatory_sources.yaml").read_text(encoding="utf-8")
    else:
        raw = Path(path).read_text(encoding="utf-8")
    data = yaml.safe_load(raw)

    frameworks = tuple(
        Framework(
            key=fw["key"],
            label=fw["label"],
            act=fw["act"],
            act_de=fw["act_de"],
            celex=str(fw["celex"]),
            oj=fw["oj"],
            consolidated_as_of=str(fw["consolidated_as_of"]),
            url=fw["url"],
            consolidated_celex=(
                str(fw["consolidated_celex"]) if fw.get("consolidated_celex") else None
            ),
            amended_by=tuple(
                Amendment(
                    act=a["act"],
                    act_de=a["act_de"],
                    celex=str(a["celex"]),
                    oj=a["oj"],
                    in_force=str(a["in_force"]),
                    note=a["note"].strip(),
                )
                for a in fw.get("amended_by", [])
            ),
            references=tuple(
                Reference(id=str(r["id"]), topic=r["topic"]) for r in fw["references"]
            ),
        )
        for fw in data["frameworks"]
    )
    verification = data["verification"]
    return Sources(
        version=data["version"],
        title=data["title"],
        frameworks=frameworks,
        documents=tuple((d["path"], d["framework"], d["lang"]) for d in data["documents"]),
        verified_at=str(verification["verified_at"]),
        verification_method=verification["method"],
        verification_sources=tuple(verification["sources"]),
        owner_verified=bool(verification["owner_verified"]),
    )


# --------------------------------------------------------------------------- #
# Scanning — what a document actually cites.
# --------------------------------------------------------------------------- #
def scan_references(text: str) -> set[str]:
    """Return the normalised reference ids cited in ``text`` ("5", "24-27", "annex-III")."""
    found: set[str] = set()
    for match in _REFERENCE.finditer(text):
        if article := match.group("article"):
            found.add(re.sub(r"\s*[–-]\s*", "-", article.strip()))
        else:
            found.add(f"annex-{match.group('annex')}")
    return found


def check_references(root: Path | None = None) -> list[str]:
    """Return one message per reference that is cited but unpinned, pinned but uncited, or cited in
    a document the source lock does not know about.

    The last case is the one that would otherwise rot silently: a bare "Art. 9" means different
    things in different acts, so an article number is only checkable in a document bound to one
    framework. Prose documents point at the checklists instead of citing articles themselves.
    """
    root = root or repo_root()
    sources = load_sources()
    problems: list[str] = []
    cited: dict[str, set[str]] = {fw.key: set() for fw in sources.frameworks}
    bound = {rel for rel, _key, _lang in sources.documents}

    for path in sorted((root / "docs").rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if rel in bound or not scan_references(path.read_text(encoding="utf-8")):
            continue
        problems.append(
            f"{rel}: cites articles but is not bound to a framework in the source lock — "
            "point at a checklist instead, or bind the document"
        )

    for rel, framework_key, _lang in sources.documents:
        path = root / rel
        if not path.is_file():
            problems.append(f"{rel}: bound to {framework_key} in the lock but does not exist")
            continue
        found = scan_references(path.read_text(encoding="utf-8"))
        cited[framework_key] |= found
        for unpinned in sorted(found - sources.framework(framework_key).reference_ids):
            problems.append(f"{rel}: cites {unpinned!r}, which the source lock does not carry")

    for fw in sources.frameworks:
        for unused in sorted(fw.reference_ids - cited[fw.key]):
            problems.append(f"{fw.key}: source lock carries {unused!r}, which no document cites")
    return problems


# --------------------------------------------------------------------------- #
# Rendering — one function per generated documentation block.
# --------------------------------------------------------------------------- #
def _render_source_lock(sources: Sources, framework: Framework, lang: str) -> str:
    if lang == "de":
        amendments = "".join(
            f"\n> Geändert durch **{a.act_de}** (CELEX {a.celex}, {_oj_de(a.oj)}), "
            f"in Kraft seit {a.in_force}."
            for a in framework.amended_by
        )
        return (
            "> **Fassungsstand.** Die Artikelverweise unten beziehen sich auf "
            f"**{framework.act_de}** "
            f"(CELEX {framework.celex}, {_oj_de(framework.oj)}) — {framework.version_line('de')}."
            f"{amendments}\n"
            f"> Zuletzt am {sources.verified_at} gegen den Text geprüft: "
            f"[EUR-Lex]({framework.url}). Festgehalten in "
            f"[`regulatory-sources.md`](regulatory-sources.md).\n"
            "> Das hält fest, **welcher Text** gilt — nicht, was er von Ihnen verlangt."
        )
    amendments = "".join(
        f"\n> Amended by **{a.act}** (CELEX {a.celex}, {a.oj}), in force {a.in_force}."
        for a in framework.amended_by
    )
    return (
        f"> **Source lock.** The article references below point at **{framework.act}** "
        f"(CELEX {framework.celex}, {framework.oj}) — {framework.version_line()}."
        f"{amendments}\n"
        f"> Last checked against the text on {sources.verified_at}: "
        f"[EUR-Lex]({framework.url}). Pinned in "
        f"[`regulatory-sources.md`](regulatory-sources.md).\n"
        "> This records **which text**, not what it requires of you."
    )


def _render_registry(sources: Sources) -> str:
    parts: list[str] = []
    for fw in sources.frameworks:
        rows = "\n".join(f"| {r.id} | {r.topic} |" for r in fw.references)
        amendments = (
            "\n".join(
                f"- **{a.act}** — CELEX {a.celex}, {a.oj}, in force {a.in_force}. {a.note}"
                for a in fw.amended_by
            )
            or "- None recorded."
        )
        parts.append(
            f"### {fw.label} — {fw.act}\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| CELEX | `{fw.celex}` |\n"
            f"| Official Journal | {fw.oj} |\n"
            f"| Version checked | {fw.version_line()} |\n"
            f"| Text | [EUR-Lex]({fw.url}) |\n\n"
            f"**Amendments incorporated**\n\n{amendments}\n\n"
            f"**Referenced in the checklists**\n\n"
            f"| Article | Subject as the checklist names it |\n|---|---|\n{rows}"
        )
    return "\n\n".join(parts)


def _render_verification(sources: Sources) -> str:
    urls = "\n".join(f"- <{url}>" for url in sources.verification_sources)
    confirmed = "confirmed by the maintainer" if sources.owner_verified else "**not yet** confirmed"
    return (
        f"Checked on **{sources.verified_at}** — {sources.verification_method}. "
        f"Entries are {confirmed} by eye against the sources below.\n\n"
        f"{urls}\n\n"
        "Commentary — law-firm notes, news articles, summaries, AI-generated review — is never "
        "the source of an entry here. Several articles repeating one Official Journal "
        "publication are one source, not several."
    )


_RENDERERS = {
    "registry": _render_registry,
    "verification": _render_verification,
}

REGISTRY_DOC = "docs/03-checklists/regulatory-sources.md"


def repo_root() -> Path:
    # regulatory.py → agent_evaluator → src → evaluator → <repo root>
    return Path(__file__).resolve().parents[3]


def _block_pattern(name: str) -> re.Pattern[str]:
    return re.compile(
        r"(?P<start><!-- GENERATED:" + re.escape(name) + r" START[^\n]*-->\n)"
        r"(?P<body>.*?)"
        r"(?P<end>\n<!-- GENERATED:" + re.escape(name) + r" END -->)",
        re.DOTALL,
    )


def render_block(name: str, sources: Sources | None = None) -> str:
    sources = sources or load_sources()
    return _RENDERERS[name](sources)


def apply_block(text: str, name: str, rendered: str) -> str:
    """Replace a GENERATED block in ``text``. Shared with the policy register."""
    pattern = _block_pattern(name)
    if not pattern.search(text):
        raise ValueError(f"no GENERATED:{name} block found in the target document")
    return pattern.sub(lambda m: m.group("start") + rendered + m.group("end"), text)


def update_docs(write: bool, root: Path | None = None) -> list[str]:
    """Regenerate (write=True) or check (write=False) every generated block. Returns the files that
    were stale (write=False) or rewritten (write=True)."""
    root = root or repo_root()
    sources = load_sources()

    targets: list[tuple[str, str, str]] = [
        (REGISTRY_DOC, "registry", render_block("registry", sources)),
        (REGISTRY_DOC, "verification", render_block("verification", sources)),
    ]
    targets += [
        (rel, "source_lock", _render_source_lock(sources, sources.framework(key), lang))
        for rel, key, lang in sources.documents
    ]

    changed: list[str] = []
    for rel in dict.fromkeys(rel for rel, _, _ in targets):
        path = root / rel
        original = path.read_text(encoding="utf-8")
        updated = original
        for target_rel, name, rendered in targets:
            if target_rel == rel:
                updated = apply_block(updated, name, rendered)
        if updated != original:
            changed.append(rel)
            if write:
                path.write_text(updated, encoding="utf-8")
    return changed


def check_docs(root: Path | None = None) -> list[str]:
    """Return the documents whose generated blocks have drifted from the source lock."""
    return update_docs(write=False, root=root)


def _main(argv: list[str]) -> int:
    write = "--write" in argv
    changed = update_docs(write=write)
    problems = check_references()
    if write:
        print("rewrote:", ", ".join(changed) if changed else "nothing (already up to date)")
    elif changed:
        print("STALE — run `python -m agent_evaluator.regulatory --write`:", ", ".join(changed))
    if problems:
        for problem in problems:
            print("UNPINNED:", problem)
        return 1
    if not write and changed:
        return 1
    print("every regulatory reference is pinned to regulatory_sources.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
