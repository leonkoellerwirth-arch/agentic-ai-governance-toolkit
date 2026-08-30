#!/usr/bin/env python3
"""Resolve CELEX identifiers to their official titles and every consolidation of them.

    scripts/resolve-acts.sh acts.txt out.json

A catalogue somebody picks from has to be right about two things: what an act is called, and which
versions of it exist. Neither is ours to invent. The titles come from the Publications Office in
its own words — `expression_title` per language — and the consolidations come from the same two
routes the consolidation check uses, merged.

Short names are the one editorial field, and the output marks them as such. "Maschinenverordnung"
is not what the act is called; it is what people call it, and a catalogue that only shows the
official title is unusable while one that only shows the short name is unsourced.

Needs the network, so it is a script and not a test.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evaluator" / "src"))
from agent_evaluator.celex import consolidated_base  # noqa: E402
from agent_evaluator.legal_status import ENDPOINT, live_resolver  # noqa: E402

LANGUAGE = "http://publications.europa.eu/resource/authority/language"
XSD = "^^<http://www.w3.org/2001/XMLSchema#string>"

TITLES = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?lang (SAMPLE(?t) AS ?title) WHERE {
  ?w cdm:resource_legal_id_celex "%%s"%s .
  ?e cdm:expression_belongs_to_work ?w .
  ?e cdm:expression_uses_language ?lang .
  ?e cdm:expression_title ?t .
  FILTER(?lang IN (<%s/DEU>, <%s/ENG>))
} GROUP BY ?lang""" % (XSD, LANGUAGE, LANGUAGE)


def ask(query: str) -> list[dict]:
    url = urllib.parse.urlencode({"format": "application/sparql-results+json"})
    body = urllib.parse.urlencode({"query": query}).encode()
    request = urllib.request.Request(
        f"{ENDPOINT}?{url}", data=body, headers={"Accept": "application/sparql-results+json"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))["results"]["bindings"]


def titles(celex: str, retries: int = 4) -> dict[str, str]:
    import time

    last: Exception | None = None
    for attempt in range(retries):
        try:
            rows = ask(TITLES % celex)
            out = {}
            for row in rows:
                code = row["lang"]["value"].rsplit("/", 1)[-1]
                out["de" if code == "DEU" else "en"] = row["title"]["value"]
            return out
        except Exception as error:
            last = error
            if attempt < retries - 1:
                time.sleep(4 * (attempt + 1))
    raise RuntimeError(last)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 64
    wanted = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    resolve = live_resolver()

    acts, failed = [], []
    for entry in wanted:
        celex = entry["celex"]
        try:
            name = titles(celex)
            versions = resolve(consolidated_base(celex))
        except Exception as error:
            # An act we could not resolve is left out, loudly. A catalogue entry with a guessed
            # title is worse than a shorter catalogue.
            failed.append({"celex": celex, "error": str(error)[:120]})
            print(f"✗ {celex}: {str(error)[:80]}", file=sys.stderr)
            continue
        if "de" not in name or "en" not in name:
            failed.append({"celex": celex, "error": "no title in both languages"})
            print(f"✗ {celex}: kein Titel in beiden Sprachen", file=sys.stderr)
            continue
        acts.append(
            {
                "celex": celex,
                "short": entry["short"],
                "domain": entry["domain"],
                "title": name,
                "versions": versions,
                "newest": versions[-1] if versions else None,
            }
        )
        print(f"✓ {celex}  {len(versions)}  {entry['short']['de']}")

    Path(argv[1]).write_text(
        json.dumps(
            {
                "_source": f"SPARQL, {ENDPOINT}",
                "_titles": "cdm:expression_title, in the source's own words, per language",
                "_short_names": "editorial — what people call the act, not what it is called",
                "_versions": "both query routes, merged; see VERIFICATION.md",
                "_resolved": date.today().isoformat(),
                "acts": acts,
                "unresolved": failed,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\n{len(acts)} aufgelöst, {len(failed)} nicht.", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
