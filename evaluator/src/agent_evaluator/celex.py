"""What a CELEX identifier is, and when one belongs to another.

These rules lived in two places and pointed in opposite directions: the register-file reader
derived a consolidated base from an act, the resolver derived an act from a consolidated base by
writing the inverse out by hand, and the register this toolkit ships validated neither. A rule
kept in two places is a rule that will disagree with itself; a rule the author does not apply to
their own data is a rule they have not tested.

Sector 3 is secondary legislation — regulations, directives, decisions. That is the only sector
this toolkit pins, and narrowing the pattern to it is deliberate: a case-law or treaty identifier
reaching a consolidation check would produce an answer about nothing.
"""

from __future__ import annotations

import re

ACT = re.compile(r"3\d{4}[A-Z]\d{4}")
CONSOLIDATED = re.compile(r"0\d{4}[A-Z]\d{4}-\d{8}")


class CelexError(ValueError):
    """An identifier that cannot be what it claims to be. Never a warning: nothing is derived."""


def consolidated_base(act: str) -> str:
    """32023R1230 -> 02023R1230 — the prefix every consolidation of that act shares."""
    if not ACT.fullmatch(act):
        raise CelexError(f"{act!r} is not a CELEX identifier of a legal act")
    return "0" + act[1:]


def act_of(base: str) -> str:
    """02023R1230 -> 32023R1230 — the inverse, so the pairing is stated once, not twice."""
    act = "3" + base[1:]
    if not ACT.fullmatch(act):
        raise CelexError(f"{base!r} is not the consolidated base of a legal act")
    return act


def check_act(celex: str, where: str) -> str:
    if not ACT.fullmatch(celex):
        raise CelexError(f"{where}: {celex!r} is not a CELEX identifier of a legal act.")
    return celex


def check_pin(pinned: str, act: str, where: str) -> str:
    """A pin has to be a consolidation of the act it sits under.

    Versions are compared as strings. Across two different works that comparison is meaningless,
    so a pin belonging elsewhere is refused rather than compared — reporting it would claim a
    currency nobody checked.
    """
    if not CONSOLIDATED.fullmatch(pinned):
        raise CelexError(f"{where}: {pinned!r} is not a consolidated CELEX (0YYYYTNNNN-YYYYMMDD).")
    if not pinned.startswith(consolidated_base(act) + "-"):
        raise CelexError(
            f"{where}: pinned {pinned} is not a consolidation of {act}. Comparing them would "
            "report a currency that was never checked."
        )
    return pinned
