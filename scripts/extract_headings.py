#!/usr/bin/env python3
"""Extract official article headings from the Cellar XHTML and write the snapshot.

Called by refresh-official-headings.sh. The declared context exceptions in the existing snapshot
are carried over — they are editorial judgements, not data, and a refresh must not silently drop
the reasons someone wrote down.
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

FRAMEWORKS = {
    "eu_ai_act": (
        "02024R1689-20260727",
        [
            "5",
            "6",
            "annex-III",
            "9",
            "10",
            "11",
            "12",
            "annex-IV",
            "13",
            "14",
            "15",
            "50",
            "51",
            "52",
            "53",
            "54",
            "55",
            "72",
            "73",
        ],
    ),
    "dora": (
        "32022R2554",
        [
            "5",
            "6",
            "9",
            "10",
            "11",
            "12",
            "17",
            "18",
            "19",
            "24",
            "25",
            "26",
            "27",
            "28",
            "29",
            "30",
        ],
    ),
}
SOURCE = (
    "Publications Office Cellar — http://publications.europa.eu/resource/celex/{CELEX} "
    "with Accept: application/xhtml+xml and Accept-Language: eng"
)


def headings(path: Path) -> dict[str, str]:
    text = html.unescape(
        re.sub(r"<[^>]+>", "\n", path.read_text(encoding="utf-8", errors="ignore"))
    )
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    found: dict[str, str] = {}
    for i, line in enumerate(lines):
        article = re.fullmatch(r"Article\s+(\d+)", line)
        if article and article.group(1) not in found:
            for candidate in lines[i + 1 : i + 4]:
                if (
                    candidate
                    and not candidate[0].isdigit()
                    and len(candidate) < 160
                    and not candidate.endswith(".")
                ):
                    found[article.group(1)] = candidate
                    break
        annex = re.fullmatch(r"ANNEX\s+([IVX]+)", line)
        if annex and f"annex-{annex.group(1)}" not in found:
            for candidate in lines[i + 1 : i + 3]:
                if candidate and len(candidate) < 200:
                    found[f"annex-{annex.group(1)}"] = candidate
                    break
    return found


def main(argv: list[str]) -> int:
    source_dir, out_path = Path(argv[1]), Path(argv[2])
    previous = (
        json.loads(out_path.read_text(encoding="utf-8")) if out_path.is_file() else {}
    )

    snapshot: dict = {
        "_source": SOURCE,
        "_why": previous.get(
            "_why",
            "The official heading of every article this toolkit cites, taken from the primary "
            "text rather than from a rendering of it.",
        ),
        "_fetched": date.today().isoformat(),
        "frameworks": {},
    }
    for key, (celex, ids) in FRAMEWORKS.items():
        found = headings(source_dir / f"{celex}.xhtml")
        missing = [i for i in ids if not found.get(i)]
        if missing:
            print(f"✗ {key}: no heading found for {missing}", file=sys.stderr)
            return 1
        snapshot["frameworks"][key] = {
            "celex": celex,
            "uri": f"http://publications.europa.eu/resource/celex/{celex}",
            "headings": {i: found[i] for i in ids},
        }

    # Editorial judgements survive a refresh.
    for field in ("_context_note", "context_allowed"):
        if field in previous:
            snapshot[field] = previous[field]

    out_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
