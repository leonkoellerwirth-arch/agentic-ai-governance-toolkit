"""The action authority matrix: what an agent may do alone, what needs a human, what is refused.

`rubric.py` answers how much control an agent needs. This module answers the question a reviewer
asks immediately afterwards and no rubric answers — what is it actually allowed to do. The matrix
is declared in ``action_authority.yaml`` and rendered into the checklist; nothing here enforces
anything, and saying so is the point. It is the boundary an implementation is measured against.

The load-bearing rule is ``escalates_at``: an action that is automatic below a band and needs a
human from that band up. The band names are checked against ``rubric.yaml``, so an escalation to
a level that does not exist fails rather than reading as a stricter rule than it is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .rubric import _apply, load_rubric, repo_root

MATRIX_PATH = Path(__file__).with_name("action_authority.yaml")
DOC = "docs/03-checklists/action-authority-matrix.md"
ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Matrix:
    title: str
    authorities: list[dict[str, Any]]
    groups: list[dict[str, Any]]
    actions: list[dict[str, Any]]


def load_matrix(path: Path | None = None) -> Matrix:
    raw = yaml.safe_load((path or MATRIX_PATH).read_text(encoding="utf-8"))
    return Matrix(
        title=raw["title"],
        authorities=raw["authorities"],
        groups=raw["groups"],
        actions=raw["actions"],
    )


def check_matrix(matrix: Matrix | None = None) -> list[str]:
    """Return one message per structural problem. Empty means the matrix holds up."""
    matrix = matrix or load_matrix()
    problems: list[str] = []

    authority_keys = {a["key"] for a in matrix.authorities}
    group_keys = {g["key"] for g in matrix.groups}
    band_levels = {band.level for band in load_rubric().bands}

    seen: set[str] = set()
    used_groups: set[str] = set()

    for action in matrix.actions:
        aid = action.get("id", "<no id>")
        if not ID_PATTERN.match(str(aid)):
            problems.append(f"{aid}: id must be kebab-case")
        if aid in seen:
            problems.append(f"{aid}: duplicate id")
        seen.add(aid)

        if action.get("group") not in group_keys:
            problems.append(f"{aid}: group '{action.get('group')}' is not declared")
        used_groups.add(action.get("group"))

        authority = action.get("authority")
        if authority not in authority_keys:
            problems.append(f"{aid}: authority '{authority}' is not declared")

        for field in ("action", "evidence", "rationale"):
            if not action.get(field):
                problems.append(f"{aid}: {field} is missing")

        escalates = action.get("escalates_at")
        if escalates is not None:
            if authority != "automatic":
                problems.append(
                    f"{aid}: escalates_at only applies to an automatic action — "
                    f"'{authority}' either already needs a human or is refused outright"
                )
            if escalates not in band_levels:
                problems.append(
                    f"{aid}: escalates_at '{escalates}' is not a band in rubric.yaml "
                    f"({sorted(band_levels)})"
                )

    for group in group_keys - used_groups:
        problems.append(f"group '{group}' is declared but has no actions")

    if not any(a.get("authority") == "forbidden" for a in matrix.actions):
        problems.append(
            "no action is forbidden — a matrix in which everything is permitted "
            "with enough approval is not a boundary"
        )

    return problems


def _authority_cell(action: dict[str, Any], authorities: list[dict[str, Any]], key: str) -> str:
    marker = {a["key"]: a["marker"] for a in authorities}
    if action["authority"] != key:
        return "–"
    if key == "automatic" and action.get("escalates_at"):
        return f"{marker[key]} *< {action['escalates_at']}*"
    return marker[key]


def render_matrix(matrix: Matrix | None = None) -> str:
    matrix = matrix or load_matrix()
    lines: list[str] = []
    for group in matrix.groups:
        rows = [a for a in matrix.actions if a["group"] == group["key"]]
        if not rows:
            continue
        lines += [
            f"### {group['label']}",
            "",
            f"{group['summary']}",
            "",
            "| Action | Automatic | Human approval | Forbidden | Evidence |",
            "|---|:---:|:---:|:---:|---|",
        ]
        for action in rows:
            cells = " | ".join(
                _authority_cell(action, matrix.authorities, key)
                for key in ("automatic", "human_approval", "forbidden")
            )
            lines.append(f"| {action['action']} | {cells} | {action['evidence']} |")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_rationales(matrix: Matrix | None = None) -> str:
    matrix = matrix or load_matrix()
    lines: list[str] = []
    for action in matrix.actions:
        rationale = " ".join(str(action["rationale"]).split())
        escalation = (
            f" Automatic below {action['escalates_at']}, human approval from there up."
            if action.get("escalates_at")
            else ""
        )
        lines.append(f"- **{action['action']}** — {rationale}{escalation}")
    return "\n".join(lines)


_RENDERERS = {
    "authority-matrix": render_matrix,
    "authority-rationales": render_rationales,
}


def update_docs(write: bool, root: Path | None = None) -> list[str]:
    """Regenerate (write=True) or check (write=False) the generated blocks in the matrix doc."""
    problems = check_matrix()
    if problems:
        raise ValueError("action_authority.yaml does not hold up:\n  " + "\n  ".join(problems))

    root = root or repo_root()
    matrix = load_matrix()
    path = root / DOC
    original = path.read_text(encoding="utf-8")
    updated = original
    for name, renderer in _RENDERERS.items():
        updated = _apply(updated, name, renderer(matrix))
    if updated == original:
        return []
    if write:
        path.write_text(updated, encoding="utf-8")
    return [DOC]
