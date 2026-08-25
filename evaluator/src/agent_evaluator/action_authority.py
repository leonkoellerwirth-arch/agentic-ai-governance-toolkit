"""The action authority matrix: what an agent may do alone, what needs a human, what is refused.

`rubric.py` answers how much control an agent needs. This module answers the question a reviewer
asks immediately afterwards and no rubric answers — what is it actually allowed to do. The matrix
is declared in ``action_authority.yaml`` and rendered into the checklist; nothing here enforces
anything, and saying so is the point. It is the boundary an implementation is measured against.

Authority depends on the action's own context, never on the agent's control band. An earlier
version escalated at a band — "automatic below C3" — which was wrong: the band is the sum of six
dimensions, so personal data can score C1 and C3 can arise with no personal data at all. The
conditional fields replaced it:

``automatic_requires``  preconditions that must all hold for an automatic action; any that fails
                        escalates the instance.
``escalates_when``      contexts in which an automatic action needs a person.
``automatic_if``        the narrow carve-out under which an action that normally needs approval
                        may run unattended.
``forbidden_when``      contexts in which an action that normally needs approval is refused.
``needs_competent_function_when``
                        contexts where any named approver is not enough and the responsible
                        function must approve — a regulatory disclosure is not signed off by
                        whoever happens to be available.

An automatic action with no preconditions at all fails validation. Blanket permission is the
failure this file exists to make visible, so it may not be expressed silently.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .rubric import _apply, repo_root

MATRIX_PATH = Path(__file__).with_name("action_authority.yaml")
DOC = "docs/03-checklists/action-authority-matrix.md"
ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

CONDITION_FIELDS = (
    "automatic_requires",
    "escalates_when",
    "automatic_if",
    "forbidden_when",
    "needs_competent_function_when",
)
# Which conditional fields make sense for which baseline. A forbidden action takes none: a
# condition on a refusal is an approval with extra steps.
ALLOWED_CONDITIONS: dict[str, tuple[str, ...]] = {
    "automatic": ("automatic_requires", "escalates_when"),
    "human_approval": ("automatic_if", "forbidden_when", "needs_competent_function_when"),
    "forbidden": (),
}


@dataclass(frozen=True)
class Matrix:
    title: str
    forbidden_criterion: str
    authorities: list[dict[str, Any]]
    groups: list[dict[str, Any]]
    actions: list[dict[str, Any]]


def load_matrix(path: Path | None = None) -> Matrix:
    raw = yaml.safe_load((path or MATRIX_PATH).read_text(encoding="utf-8"))
    return Matrix(
        title=raw["title"],
        forbidden_criterion=raw.get("forbidden_criterion", ""),
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

    if not str(matrix.forbidden_criterion).strip():
        problems.append("forbidden_criterion is missing — without it, 'forbidden' is a preference")

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

        allowed = ALLOWED_CONDITIONS.get(authority, ())
        for field in CONDITION_FIELDS:
            if action.get(field) and field not in allowed:
                problems.append(
                    f"{aid}: {field} does not apply to a '{authority}' action — "
                    f"only {allowed or 'no conditions'} do"
                )

        if authority == "automatic" and not action.get("automatic_requires"):
            problems.append(
                f"{aid}: an automatic action needs at least one precondition — "
                "blanket permission is the failure this matrix exists to make visible"
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
    if action.get("automatic_requires") or action.get("escalates_when"):
        return f"{marker[key]}\u2009*"
    if action.get("automatic_if") or action.get("forbidden_when"):
        return f"{marker[key]}\u2009*"
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
        lines.append(f"- **{action['action']}** — {rationale}")
        for field, lead in CONDITION_LEADS:
            for condition in action.get(field, []) or []:
                lines.append(f"  - *{lead}* {' '.join(str(condition).split())}")
    return "\n".join(lines)


CONDITION_LEADS = (
    ("automatic_requires", "Automatic only while:"),
    ("escalates_when", "Needs a person when:"),
    ("automatic_if", "May run unattended if:"),
    ("forbidden_when", "Refused when:"),
    ("needs_competent_function_when", "Needs the responsible function, not any approver, when:"),
)

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
