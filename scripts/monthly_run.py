#!/usr/bin/env python3
"""The monthly run: one record per register, with the evidence it rests on, signed and chained.

    scripts/monthly-run.sh --registers ../registers --out ../runs [--key ~/.keys/rechtsstand.pem]

A record says "a newer consolidation exists". Six months later the only way to show that was true
is the answer the source actually gave, so every run writes the raw SPARQL answers beside the
record. A record that keeps the conclusion and discards the evidence asks to be believed.

Three properties make the output usable in a review, and each is one line of work:

**Signed.** Ed25519 over the manifest. Without it, anything in the directory can be edited
afterwards and nobody can tell — which makes the whole artifact a statement of trust rather than
evidence. The key never enters this repository; it is passed in.

**Chained.** Each manifest names the digest of the previous run's manifest. Editing an old record
then breaks every later one, so tampering has to be complete or it is visible. This is what turns
a folder of files into a ledger.

**Complete about its own failures.** A register whose acts could not be checked still produces a
record, and that record says so. A run that quietly skips the month is worse than a run that
reports a gap, because the gap is what the reader needs to act on.

This is deliberately not a service platform. Tenancy is the file name. For a handful of registers
that is the honest amount of machinery, and it stays auditable by one person.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evaluator" / "src"))
from agent_evaluator import __version__  # noqa: E402
from agent_evaluator.legal_status import (  # noqa: E402
    ENDPOINT,
    build_profile_record,
    live_resolver,
    render_markdown,
)

LEDGER = "legal-status-ledger"
LEDGER_VERSION = "1.0.0"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sign(manifest_file: Path, key: Path | None, out: Path) -> dict[str, str] | None:
    """Ed25519 over the manifest FILE, via openssl.

    The file and not a pipe: Ed25519 signs in one shot and openssl needs to know the length up
    front, so stdin fails with "unable to determine file size". Signing the file that is actually
    written is also the honest order — what gets signed is what a reader will later verify.

    No key, no signature. The manifest then says `unsigned` rather than pretending.
    """
    if key is None:
        return None
    signature = out / "manifest.sig"
    try:
        subprocess.run(
            [
                "openssl", "pkeyutl", "-sign", "-inkey", str(key),
                "-rawin", "-in", str(manifest_file), "-out", str(signature),
            ],
            check=True,
            capture_output=True,
        )
        public = subprocess.run(
            ["openssl", "pkey", "-in", str(key), "-pubout"],
            check=True,
            capture_output=True,
        ).stdout
        (out / "public-key.pem").write_bytes(public)
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        # A signature we could not produce is recorded as absent, never faked and never silent.
        print(f"✗ signing failed: {error}", file=sys.stderr)
        return None
    return {
        "algorithm": "Ed25519",
        "signature_file": "manifest.sig",
        "public_key_file": "public-key.pem",
    }


def previous_manifest(runs: Path) -> dict[str, str] | None:
    """The newest manifest already written. Its digest is what the next one commits to."""
    manifests = sorted(runs.glob("*/*/manifest.json"))
    if not manifests:
        return None
    last = manifests[-1]
    return {"path": str(last.relative_to(runs)), "sha256": digest(last.read_bytes())}


def run_one(register: Path, out: Path, stamp: str) -> dict[str, object]:
    evidence = out / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    written: list[dict[str, str]] = []

    def sink(route: str, query: str, raw: str) -> None:
        name = f"{route}-{len(written):02d}.json"
        (evidence / name).write_text(raw, encoding="utf-8")
        written.append(
            {
                "file": f"evidence/{name}",
                "route": route,
                "query": query,
                "sha256": digest(raw.encode("utf-8")),
            }
        )

    record = build_profile_record(register, resolve=live_resolver(sink=sink))
    (out / "record.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for lang in ("de", "en"):
        (out / f"record.{lang}.md").write_text(render_markdown(record, lang), encoding="utf-8")

    superseded = [a["key"] for a in record["acts"] if a["status"] == "superseded"]
    unchecked = [a["key"] for a in record["acts"] if a["status"] == "unchecked"]
    return {
        "register": register.name,
        "register_sha256": digest(register.read_bytes()),
        "prepared_on": stamp,
        "acts": len(record["acts"]),
        "superseded": superseded,
        "unchecked": unchecked,
        # The verdict a reader acts on. Superseded forces work; unchecked means the run left a
        # question open and must not read as a clean month.
        "verdict": "superseded" if superseded else ("unchecked" if unchecked else "clean"),
        "artifacts": [
            {"file": name, "sha256": digest((out / name).read_bytes())}
            for name in ("record.json", "record.de.md", "record.en.md")
        ],
        "evidence": written,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registers", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--key", type=Path, default=None)
    parser.add_argument("--month", default=None, help="YYYY-MM; defaults to today's month.")
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    month = args.month or now.strftime("%Y-%m")
    stamp = now.date().isoformat()

    registers = sorted(p for p in args.registers.glob("*.yaml") if p.is_file())
    if not registers:
        print(f"✗ no register files in {args.registers}", file=sys.stderr)
        return 2

    chain = previous_manifest(args.out)
    results, failures = [], []
    for register in registers:
        out = args.out / month / register.stem
        out.mkdir(parents=True, exist_ok=True)
        try:
            result = run_one(register, out, stamp)
        except Exception as error:  # a register that fails must not take the month down
            failures.append({"register": register.name, "error": str(error)[:200]})
            print(f"✗ {register.name}: {str(error)[:100]}", file=sys.stderr)
            continue
        results.append(result)
        print(f"✓ {register.name}: {result['verdict']} ({result['acts']} acts)")

        manifest = {
            "ledger": LEDGER,
            "ledger_version": LEDGER_VERSION,
            "tool": {"name": "agent-eval", "version": __version__},
            "source": ENDPOINT,
            "produced_at": now.isoformat(),
            "month": month,
            "previous": chain,
            "run": result,
        }
        body = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        manifest_file = out / "manifest.json"
        manifest_file.write_bytes(body)
        # The signature covers manifest.json byte for byte. It is kept beside it rather than
        # inside it: a document cannot carry a signature over itself, and a reader who has to
        # reconstruct which bytes were signed will eventually reconstruct them wrong.
        signature = sign(manifest_file, args.key, out)
        (out / "signature.json").write_text(
            json.dumps(
                {
                    "covers": "manifest.json",
                    "sha256": digest(body),
                    **(signature or {"algorithm": None, "note": "unsigned"}),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        chain = {
            "path": str((out / "manifest.json").relative_to(args.out)),
            "sha256": digest(body),
        }

    print(
        f"\n{len(results)} record(s), {len(failures)} failed. "
        f"Verdicts: {', '.join(r['verdict'] for r in results) or '—'}",
        file=sys.stderr,
    )
    if failures:
        return 2
    return 1 if any(r["verdict"] != "clean" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
