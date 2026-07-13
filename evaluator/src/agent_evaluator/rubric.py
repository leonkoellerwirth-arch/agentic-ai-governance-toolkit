"""Load, model, and render the control-intensity rubric.

``rubric.yaml`` (shipped as package data) is the single source of truth. This module reads it, and
it also renders the Markdown tables in the ``docs/02-risk-assessment/`` files, so the documentation
can never drift from the rubric the code uses:

- ``python -m agent_evaluator.rubric --write``  regenerates the doc tables from the YAML.
- ``python -m agent_evaluator.rubric --check``  exits non-zero if any doc table is stale.

The consistency test (``tests/test_rubric_consistency.py``) calls :func:`check_docs`.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import yaml

# Control levels, lowest to highest. Used to order bands and to apply override floors.
LEVEL_ORDER: tuple[str, ...] = ("C1", "C2", "C3", "C4")


@dataclass(frozen=True)
class Dimension:
    key: str
    label: str
    question: str
    anchors: dict[int, str]


@dataclass(frozen=True)
class Band:
    level: str
    name: str
    min: int
    max: int
    summary: str


@dataclass(frozen=True)
class Override:
    dimension: str
    at_least: int
    floor: str
    reason: str


@dataclass(frozen=True)
class Rubric:
    version: int
    title: str
    scale_min: int
    scale_max: int
    dimensions: tuple[Dimension, ...]
    bands: tuple[Band, ...]
    overrides: tuple[Override, ...]
    controls: dict[str, tuple[str, ...]]

    @property
    def dimension_keys(self) -> tuple[str, ...]:
        return tuple(d.key for d in self.dimensions)

    def band_for_total(self, total: int) -> Band:
        for band in self.bands:
            if band.min <= total <= band.max:
                return band
        raise ValueError(f"total {total} is outside every band range")


def load_rubric(path: str | Path | None = None) -> Rubric:
    """Load the rubric from ``path`` (defaults to the packaged ``rubric.yaml``)."""
    if path is None:
        raw = (files("agent_evaluator") / "rubric.yaml").read_text(encoding="utf-8")
    else:
        raw = Path(path).read_text(encoding="utf-8")
    data = yaml.safe_load(raw)

    dimensions = tuple(
        Dimension(
            key=d["key"],
            label=d["label"],
            question=d["question"],
            anchors={int(k): v for k, v in d["anchors"].items()},
        )
        for d in data["dimensions"]
    )
    agg = data["aggregation"]
    bands = tuple(
        Band(level=b["level"], name=b["name"], min=b["min"], max=b["max"], summary=b["summary"])
        for b in agg["bands"]
    )
    overrides = tuple(
        Override(
            dimension=o["dimension"],
            at_least=o["at_least"],
            floor=o["floor"],
            reason=o["reason"],
        )
        for o in agg.get("overrides", [])
    )
    controls = {level: tuple(items) for level, items in data["controls"].items()}
    return Rubric(
        version=data["version"],
        title=data["title"],
        scale_min=data["scale"]["min"],
        scale_max=data["scale"]["max"],
        dimensions=dimensions,
        bands=bands,
        overrides=overrides,
        controls=controls,
    )


# --------------------------------------------------------------------------- #
# Rendering — one function per generated documentation block.
# --------------------------------------------------------------------------- #
def _render_dimensions(r: Rubric) -> str:
    parts: list[str] = []
    for d in r.dimensions:
        rows = "\n".join(f"| {score} | {d.anchors[score]} |" for score in sorted(d.anchors))
        parts.append(
            f"### {d.label}\n\n_{d.question}_\n\n| Score | Anchor |\n|:-----:|--------|\n{rows}"
        )
    return "\n\n".join(parts)


def _render_bands(r: Rubric) -> str:
    rows = "\n".join(f"| {b.level} | {b.name} | {b.min}–{b.max} | {b.summary} |" for b in r.bands)
    return (
        "| Level | Name | Total score | What it means |\n"
        "|:-----:|------|:-----------:|---------------|\n"
        f"{rows}"
    )


def _render_overrides(r: Rubric) -> str:
    rows = []
    for o in r.overrides:
        dim = o.dimension.replace("_", " ").capitalize()
        rows.append(f"| {dim} | ≥ {o.at_least} | {o.floor} | {o.reason} |")
    return (
        "| Dimension | Condition | Raises floor to | Why |\n"
        "|-----------|:---------:|:---------------:|-----|\n" + "\n".join(rows)
    )


def _render_controls(r: Rubric) -> str:
    by_level = {b.level: b for b in r.bands}
    parts: list[str] = []
    for level in LEVEL_ORDER:
        if level not in r.controls:
            continue
        band = by_level[level]
        bullets = "\n".join(f"- {item}" for item in r.controls[level])
        parts.append(f"#### {level} — {band.name} (score {band.min}–{band.max})\n\n{bullets}")
    return "\n\n".join(parts)


_RENDERERS = {
    "dimensions": _render_dimensions,
    "bands": _render_bands,
    "overrides": _render_overrides,
    "controls": _render_controls,
}

# Which generated blocks live in which documentation file (repo-root-relative).
DOC_BLOCKS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("docs/02-risk-assessment/agent-risk-model.md", ("dimensions",)),
    ("docs/02-risk-assessment/scoring-rubric.md", ("bands", "overrides", "controls")),
)


def repo_root() -> Path:
    # rubric.py → agent_evaluator → src → evaluator → <repo root>
    return Path(__file__).resolve().parents[3]


def _block_pattern(name: str) -> re.Pattern[str]:
    return re.compile(
        r"(?P<start><!-- GENERATED:" + re.escape(name) + r" START[^\n]*-->\n)"
        r"(?P<body>.*?)"
        r"(?P<end>\n<!-- GENERATED:" + re.escape(name) + r" END -->)",
        re.DOTALL,
    )


def render_block(name: str, rubric: Rubric | None = None) -> str:
    rubric = rubric or load_rubric()
    return _RENDERERS[name](rubric)


def _apply(text: str, name: str, rendered: str) -> str:
    pattern = _block_pattern(name)
    if not pattern.search(text):
        raise ValueError(f"no GENERATED:{name} block found in the target document")
    return pattern.sub(lambda m: m.group("start") + rendered + m.group("end"), text)


def update_docs(write: bool, root: Path | None = None) -> list[str]:
    """Regenerate (write=True) or check (write=False) every doc block. Returns the list of files
    that were stale (write=False) or rewritten (write=True)."""
    root = root or repo_root()
    rubric = load_rubric()
    changed: list[str] = []
    for rel, blocks in DOC_BLOCKS:
        path = root / rel
        original = path.read_text(encoding="utf-8")
        updated = original
        for name in blocks:
            updated = _apply(updated, name, render_block(name, rubric))
        if updated != original:
            changed.append(rel)
            if write:
                path.write_text(updated, encoding="utf-8")
    return changed


def check_docs(root: Path | None = None) -> list[str]:
    """Return the list of documentation files whose generated tables have drifted from the YAML."""
    return update_docs(write=False, root=root)


def _main(argv: list[str]) -> int:
    write = "--write" in argv
    check = "--check" in argv or not write
    changed = update_docs(write=write)
    if write:
        if changed:
            print("rewrote:", ", ".join(changed))
        else:
            print("docs already up to date")
        return 0
    if check and changed:
        print("STALE — run `python -m agent_evaluator.rubric --write`:", ", ".join(changed))
        return 1
    print("docs are consistent with rubric.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
