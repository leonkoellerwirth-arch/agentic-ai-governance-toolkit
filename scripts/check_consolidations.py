#!/usr/bin/env python3
"""Ask the Publications Office whether a newer consolidated version exists.

The source lock pins a consolidated text. Pinning is what makes a citation checkable — and it is
also what makes the register go quietly stale, because a pin never notices that the law moved. This
closes that: the SPARQL endpoint at the Publications Office lists every consolidated version of a
work, and a consolidation newer than the pin is a finding.

    scripts/check-consolidations.sh            # query, compare, report
    scripts/check-consolidations.sh --write    # also refresh the committed snapshot

Needs the network, so it is a script and not a test. The gate compares the pin against the
committed snapshot instead, and stays offline.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "evaluator" / "src" / "agent_evaluator" / "regulatory_sources.yaml"
SNAPSHOT = ROOT / "evaluator" / "src" / "agent_evaluator" / "consolidations.json"
ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"

QUERY = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex WHERE {
  ?w cdm:resource_legal_id_celex ?celex .
  FILTER(STRSTARTS(STR(?celex), "%s"))
} ORDER BY ?celex"""


def consolidated_base(celex: str) -> str:
    """32024R1689 -> 02024R1689. Consolidated CELEX ids carry a leading 0 and a date suffix."""
    return (
        "0" + celex[1:]
        if re.fullmatch(r"3\d{4}[A-Z]\d{4}", celex)
        else celex.split("-")[0]
    )


def versions(base: str) -> list[str]:
    url = f"{ENDPOINT}?{urllib.parse.urlencode({'format': 'application/sparql-results+json'})}"
    body = urllib.parse.urlencode({"query": QUERY % base}).encode()
    request = urllib.request.Request(
        url, data=body, headers={"Accept": "application/sparql-results+json"}
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return sorted(row["celex"]["value"] for row in payload["results"]["bindings"])


def main(argv: list[str]) -> int:
    write = "--write" in argv
    register = yaml.safe_load(REGISTER.read_text(encoding="utf-8"))

    findings: list[str] = []
    snapshot = {
        "_source": f"SPARQL, {ENDPOINT} — every consolidated version of the pinned work",
        "_why": (
            "A pin makes a citation checkable and never notices that the law moved. This records "
            "which consolidations exist, so the gate can tell when the pin has fallen behind."
        ),
        "_checked": date.today().isoformat(),
        "frameworks": {},
    }

    for framework in register["frameworks"]:
        key = framework["key"]
        base = consolidated_base(str(framework["celex"]))
        pinned = str(framework.get("consolidated_celex") or "")
        try:
            available = versions(base)
        except Exception as error:  # network, endpoint, malformed answer
            print(f"✗ {key}: could not reach the endpoint — {error}", file=sys.stderr)
            return 2

        snapshot["frameworks"][key] = {
            "base": base,
            "pinned": pinned or None,
            "available": available,
        }

        newest = available[-1] if available else ""
        if not pinned:
            if available:
                findings.append(
                    f"{key}: pins the base act, but consolidated versions exist ({', '.join(available)}). "
                    "Citations resolve against a text that may already have been amended."
                )
        elif newest and newest > pinned:
            findings.append(
                f"{key}: pinned {pinned}, but {newest} exists. The register cites a superseded text."
            )
        else:
            print(f"✓ {key}: {pinned or base} is the newest consolidation")

    if write:
        SNAPSHOT.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {SNAPSHOT.relative_to(ROOT)}")

    if findings:
        print("\nconsolidation findings:", file=sys.stderr)
        for finding in findings:
            print(f"  {finding}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
