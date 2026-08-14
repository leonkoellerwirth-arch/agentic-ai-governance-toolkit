"""Load, model, and render the policy-decision register.

Every threshold in a rubric is either **derived** — traceable to a demand the toolkit already makes,
recorded in the rubric itself — or a **policy decision**: a judgement call, recorded in
``policy_decisions.yaml`` with its rationale and the cost it accepts. Nothing may be neither.

The thresholds that need covering are computed from the rubric files themselves, so:

- adding a band or an override without recording the decision fails the check;
- a decision pointing at a threshold that no longer exists fails it too.

- ``python -m agent_evaluator.policy --write``  regenerates the register doc.
- ``python -m agent_evaluator.policy --check``  exits non-zero if stale or uncovered.

The consistency test (``tests/test_policy_decisions.py``) calls :func:`check_coverage` and
:func:`check_docs`.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import yaml

from .regulatory import apply_block, repo_root

REGISTER_DOC = "docs/02-risk-assessment/policy-decisions.md"

# Which rubric files carry thresholds, and how to enumerate them. A file only counts once it is in
# the package — the readiness rubric joins this map when it lands, and cannot land without its
# decisions, because its targets become required the moment the file exists.
RUBRIC_FILES: tuple[str, ...] = ("rubric.yaml", "readiness.yaml")


@dataclass(frozen=True)
class Decision:
    id: str
    target: str
    decision: str
    rationale: tuple[str, ...]
    external_support: tuple[str, ...]
    accepted_cost: str
    status: str


@dataclass(frozen=True)
class Register:
    version: int
    title: str
    decisions: tuple[Decision, ...]

    @property
    def targets(self) -> frozenset[str]:
        return frozenset(d.target for d in self.decisions)


def load_register(path: str | Path | None = None) -> Register:
    """Load the register from ``path`` (defaults to the packaged ``policy_decisions.yaml``)."""
    if path is None:
        raw = (files("agent_evaluator") / "policy_decisions.yaml").read_text(encoding="utf-8")
    else:
        raw = Path(path).read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    decisions = tuple(
        Decision(
            id=d["id"],
            target=d["target"],
            decision=d["decision"].strip(),
            rationale=tuple(r.strip() for r in d["rationale"]),
            external_support=tuple(d.get("external_support") or ()),
            accepted_cost=d["accepted_cost"].strip(),
            status=d["status"],
        )
        for d in data["decisions"]
    )
    return Register(version=data["version"], title=data["title"], decisions=decisions)


def required_targets() -> list[str]:
    """Enumerate the thresholds that must be covered, read off the rubric files that exist."""
    required: list[str] = []
    for name in RUBRIC_FILES:
        resource = files("agent_evaluator") / name
        if not resource.is_file():
            continue
        data = yaml.safe_load(resource.read_text(encoding="utf-8"))
        required.append(f"{name}#dimensions")
        required.append(f"{name}#scale")
        aggregation = data.get("aggregation") or {}
        if "method" in aggregation:
            required.append(f"{name}#aggregation.method")
        if "bands" in aggregation:
            required.append(f"{name}#aggregation.bands")
        for override in aggregation.get("overrides", []):
            required.append(f"{name}#aggregation.overrides.{override['dimension']}")
        # The readiness rubric carries a required level per control level, per dimension: each is a
        # judgement about how much control a given exposure demands.
        for dimension in data.get("dimensions", []):
            if "required" in dimension:
                required.append(f"{name}#dimensions.{dimension['key']}.required")
        for key in ("aggregation.per_dimension", "aggregation.exposure"):
            section, _, field = key.partition(".")
            if field in (data.get(section) or {}):
                required.append(f"{name}#{key}")
    return required


def check_coverage() -> list[str]:
    """Return one message per threshold with no recorded decision, or decision with no threshold."""
    register = load_register()
    required = required_targets()
    problems = [
        f"{target}: a threshold with no recorded decision — derive it, or record why it is chosen"
        for target in required
        if target not in register.targets
    ]
    problems += [
        f"{decision.id}: targets {decision.target!r}, which no rubric carries any more"
        for decision in register.decisions
        if decision.target not in required
    ]
    return problems


def _render_decisions(register: Register) -> str:
    parts: list[str] = []
    for d in register.decisions:
        rationale = "\n".join(f"- {line}" for line in d.rationale)
        support = (
            "\n".join(f"- {item}" for item in d.external_support)
            if d.external_support
            else "- None. This is a judgement call, and is recorded as one."
        )
        parts.append(
            f"### {d.id} — {d.decision}\n\n"
            f"**Applies to** `{d.target}` · **status** `{d.status}`\n\n"
            f"**Why**\n\n{rationale}\n\n"
            f"**Support outside this project**\n\n{support}\n\n"
            f"**What it accepts as a cost**\n\n{d.accepted_cost}"
        )
    return "\n\n".join(parts)


def _render_coverage(register: Register) -> str:
    required = required_targets()
    by_target = {d.target: d for d in register.decisions}
    rows = "\n".join(
        f"| `{target}` | {by_target[target].id if target in by_target else '**uncovered**'} |"
        for target in required
    )
    return (
        f"{len(required)} thresholds carry a judgement; "
        f"{len(register.decisions)} decisions are recorded.\n\n"
        f"| Threshold | Decision |\n|---|---|\n{rows}"
    )


_RENDERERS = {
    "policy_decisions": _render_decisions,
    "policy_coverage": _render_coverage,
}


def render_block(name: str, register: Register | None = None) -> str:
    register = register or load_register()
    return _RENDERERS[name](register)


def update_docs(write: bool, root: Path | None = None) -> list[str]:
    """Regenerate (write=True) or check (write=False) the register doc."""
    root = root or repo_root()
    register = load_register()
    path = root / REGISTER_DOC
    original = path.read_text(encoding="utf-8")
    updated = original
    for name in _RENDERERS:
        updated = apply_block(updated, name, render_block(name, register))
    if updated == original:
        return []
    if write:
        path.write_text(updated, encoding="utf-8")
    return [REGISTER_DOC]


def check_docs(root: Path | None = None) -> list[str]:
    """Return the register doc if it has drifted from the YAML."""
    return update_docs(write=False, root=root)


def _main(argv: list[str]) -> int:
    write = "--write" in argv
    changed = update_docs(write=write)
    problems = check_coverage()
    if write:
        print("rewrote:", ", ".join(changed) if changed else "nothing (already up to date)")
    elif changed:
        print("STALE — run `python -m agent_evaluator.policy --write`:", ", ".join(changed))
    if problems:
        for problem in problems:
            print("UNCOVERED:", problem)
        return 1
    if not write and changed:
        return 1
    print("every rubric threshold is either derived or a recorded decision")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
