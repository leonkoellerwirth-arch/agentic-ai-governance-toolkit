#!/usr/bin/env python3
"""Verify a monthly run: signature, digests, and the link to the run before it.

    scripts/verify-run.sh ../runs/2026-08/maschinenbau

Evidence that only its author can check is not evidence. This is the command an internal auditor
runs, and it needs no knowledge of openssl flags and no access to anything but the directory.

It checks four things, and reports each separately because they fail for different reasons:

  signature  — manifest.json is byte-for-byte what was signed. A failure means someone edited it.
  artifacts  — the record files still hash to what the manifest recorded.
  evidence   — the raw source answers still hash to what the manifest recorded. This is the one
               that matters six months later: the conclusion is only worth the answer it rests on.
  chain      — the previous run's manifest still hashes to what this one committed to. Editing an
               old month then breaks every later one, so tampering has to be complete or visible.

Exit: 0 all four hold · 1 something does not · 2 the directory is not a run.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_signature(run: Path, manifest: bytes) -> tuple[bool, str]:
    meta_file = run / "signature.json"
    if not meta_file.is_file():
        return False, "no signature.json — this run was never signed"
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    if meta.get("sha256") != digest(manifest):
        return False, "signature.json records a different digest than manifest.json has"
    if not meta.get("algorithm"):
        # An unsigned run is not a failed verification; it is a run that never claimed to be
        # verifiable. Saying so plainly is the point.
        return False, "recorded as unsigned"
    key = run / str(meta.get("public_key_file", "public-key.pem"))
    sig = run / str(meta.get("signature_file", "manifest.sig"))
    if not key.is_file() or not sig.is_file():
        return False, "signature or public key file missing"
    try:
        subprocess.run(
            [
                "openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(key),
                "-rawin", "-in", str(run / "manifest.json"), "-sigfile", str(sig),
            ],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        return False, f"openssl says no ({type(error).__name__})"
    # The key travels with the run, so this proves integrity, not identity: it says the files were
    # not edited after signing, not who signed them. Whoever relies on it needs the public key
    # from somewhere other than the directory it validates.
    return True, "valid (key from the run directory — proves integrity, not identity)"


def check_digests(run: Path, entries: list[dict], label: str) -> tuple[bool, str]:
    missing, changed = [], []
    for entry in entries:
        path = run / str(entry["file"])
        if not path.is_file():
            missing.append(entry["file"])
        elif digest(path.read_bytes()) != entry["sha256"]:
            changed.append(entry["file"])
    if missing or changed:
        parts = []
        if missing:
            parts.append(f"{len(missing)} missing ({', '.join(missing[:3])})")
        if changed:
            parts.append(f"{len(changed)} changed ({', '.join(changed[:3])})")
        return False, "; ".join(parts)
    return True, f"{len(entries)} {label} intact"


def check_chain(run: Path, manifest: dict) -> tuple[bool, str]:
    previous = manifest.get("previous")
    if not previous:
        return True, "first run in this ledger — nothing to chain to"
    # runs/<month>/<register>/manifest.json → the ledger root is two levels up.
    root = run.parent.parent
    target = root / str(previous["path"])
    if not target.is_file():
        return False, f"the run it chains to is gone ({previous['path']})"
    if digest(target.read_bytes()) != previous["sha256"]:
        return False, f"the run it chains to has been edited ({previous['path']})"
    return True, f"links to {previous['path']}"


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 64
    run = Path(argv[0])
    manifest_file = run / "manifest.json"
    if not manifest_file.is_file():
        print(f"✗ {run} holds no manifest.json — not a run directory", file=sys.stderr)
        return 2
    raw = manifest_file.read_bytes()
    manifest = json.loads(raw.decode("utf-8"))
    result = manifest.get("run", {})

    checks = [
        ("signature", *check_signature(run, raw)),
        ("artifacts", *check_digests(run, result.get("artifacts", []), "artifacts")),
        ("evidence", *check_digests(run, result.get("evidence", []), "source answers")),
        ("chain", *check_chain(run, manifest)),
    ]
    for name, ok, detail in checks:
        print(f"  {'✓' if ok else '✗'} {name:<10} {detail}")

    print(
        f"\n  register {result.get('register')} · {result.get('acts')} acts · "
        f"verdict {result.get('verdict')} · prepared {result.get('prepared_on')}"
    )
    failed = [name for name, ok, _ in checks if not ok]
    if failed:
        print(f"\n✗ not verified: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("\n✓ verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
