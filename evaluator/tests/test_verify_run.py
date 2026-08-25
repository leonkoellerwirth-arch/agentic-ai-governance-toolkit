"""The verifier itself — because a check that silently passes everything looks exactly like a
check that works.

`scripts/verify-run.sh` is what an internal auditor runs against a monthly run. Its whole value is
that it says no when something was edited, and that failure mode is invisible from the outside: a
verifier which returns "verified" unconditionally reads identically to one that verified.

Each test here edits exactly one thing in a run directory and requires that the corresponding check
— and only it — refuses. The four are kept apart deliberately: an artifact changed, a source answer
changed, the manifest changed, and the previous month changed are four different accusations, and
telling a reader which one applies is the difference between a finding and an alarm.

Offline: the fixture is built here, not fetched. Signing needs openssl and is skipped where it is
absent, but the digest and chain checks are exercised either way.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_run  # noqa: E402


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _openssl() -> bool:
    return shutil.which("openssl") is not None


def build_run(root: Path, name: str = "register", previous: dict | None = None) -> Path:
    """A minimal but structurally honest run: two artifacts, two source answers, a manifest."""
    run = root / "2026-08" / name
    (run / "evidence").mkdir(parents=True, exist_ok=True)
    (run / "record.json").write_text('{"acts": []}\n', encoding="utf-8")
    (run / "record.de.md").write_text("# Rechtsstandsbeleg\n", encoding="utf-8")
    (run / "evidence" / "prefix-00.json").write_text('{"results": {"bindings": []}}', "utf-8")
    (run / "evidence" / "relation-01.json").write_text('{"results": {"bindings": []}}', "utf-8")

    manifest = {
        "ledger": "legal-status-ledger",
        "previous": previous,
        "run": {
            "register": f"{name}.yaml",
            "acts": 0,
            "verdict": "clean",
            "prepared_on": "2026-08-26",
            "artifacts": [
                {"file": f, "sha256": sha((run / f).read_bytes())}
                for f in ("record.json", "record.de.md")
            ],
            "evidence": [
                {"file": f, "sha256": sha((run / f).read_bytes())}
                for f in ("evidence/prefix-00.json", "evidence/relation-01.json")
            ],
        },
    }
    body = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    (run / "manifest.json").write_bytes(body)

    signature: dict[str, object] = {"algorithm": None, "note": "unsigned"}
    if _openssl():
        key = run / "key.pem"
        subprocess.run(
            ["openssl", "genpkey", "-algorithm", "ed25519", "-out", str(key)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "openssl",
                "pkeyutl",
                "-sign",
                "-inkey",
                str(key),
                "-rawin",
                "-in",
                str(run / "manifest.json"),
                "-out",
                str(run / "manifest.sig"),
            ],
            check=True,
            capture_output=True,
        )
        public = subprocess.run(
            ["openssl", "pkey", "-in", str(key), "-pubout"], check=True, capture_output=True
        ).stdout
        (run / "public-key.pem").write_bytes(public)
        key.unlink()
        signature = {
            "algorithm": "Ed25519",
            "signature_file": "manifest.sig",
            "public_key_file": "public-key.pem",
        }
    (run / "signature.json").write_text(
        json.dumps({"covers": "manifest.json", "sha256": sha(body), **signature}, indent=2),
        encoding="utf-8",
    )
    return run


def verdicts(run: Path) -> dict[str, bool]:
    raw = (run / "manifest.json").read_bytes()
    manifest = json.loads(raw.decode("utf-8"))
    result = manifest.get("run", {})
    return {
        "signature": verify_run.check_signature(run, raw)[0],
        "artifacts": verify_run.check_digests(run, result["artifacts"], "artifacts")[0],
        "evidence": verify_run.check_digests(run, result["evidence"], "answers")[0],
        "chain": verify_run.check_chain(run, manifest)[0],
    }


def test_an_untouched_run_verifies(tmp_path):
    run = build_run(tmp_path)
    assert all(verdicts(run).values())
    assert verify_run.main([str(run)]) == 0


def test_an_edited_record_fails_only_the_artifact_check(tmp_path):
    """Which accusation applies is the difference between a finding and an alarm."""
    run = build_run(tmp_path)
    (run / "record.de.md").write_text("# Etwas anderes\n", encoding="utf-8")
    assert verdicts(run) | {"artifacts": False} == verdicts(run)
    assert verdicts(run)["evidence"] and verdicts(run)["chain"]
    assert verify_run.main([str(run)]) == 1


def test_an_edited_source_answer_fails_the_evidence_check(tmp_path):
    """The one that matters six months later: a conclusion is worth the answer it rests on."""
    run = build_run(tmp_path)
    (run / "evidence" / "prefix-00.json").write_text('{"results": {"bindings": [1]}}', "utf-8")
    checks = verdicts(run)
    assert checks["evidence"] is False
    assert checks["artifacts"] is True


def test_an_edited_manifest_fails_the_signature_check(tmp_path):
    run = build_run(tmp_path)
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    manifest["run"]["verdict"] = "clean"
    manifest["run"]["acts"] = 99  # a value it did NOT already hold
    (run / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    assert verdicts(run)["signature"] is False


def test_a_tamper_test_that_changes_nothing_proves_nothing(tmp_path):
    """Written because the first attempt at the test above did exactly this and passed.

    Rewriting a field to the value it already held leaves the bytes identical, the signature
    verifies, and the test reports success while checking nothing. The guard is cheap: assert the
    bytes actually moved before believing what the verifier says about them.
    """
    run = build_run(tmp_path)
    before = (run / "manifest.json").read_bytes()
    manifest = json.loads(before.decode("utf-8"))
    manifest["run"]["verdict"] = "clean"  # already "clean"
    after = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    assert after == before
    assert verdicts(run)["signature"] is True


def test_an_edited_earlier_month_breaks_the_chain(tmp_path):
    """Editing an old run then breaks every later one — tampering has to be complete or visible."""
    first = build_run(tmp_path, "alpha")
    previous = {
        "path": str((first / "manifest.json").relative_to(tmp_path)),
        "sha256": sha((first / "manifest.json").read_bytes()),
    }
    second = build_run(tmp_path, "beta", previous=previous)
    assert verdicts(second)["chain"] is True

    (first / "manifest.json").write_text('{"run": {}}', encoding="utf-8")
    assert verdicts(second)["chain"] is False
    assert verify_run.main([str(second)]) == 1


def test_a_missing_previous_run_is_a_broken_chain_not_a_fresh_start(tmp_path):
    """Deleting the month you chained to must not look like being the first run."""
    first = build_run(tmp_path, "alpha")
    previous = {
        "path": str((first / "manifest.json").relative_to(tmp_path)),
        "sha256": sha((first / "manifest.json").read_bytes()),
    }
    second = build_run(tmp_path, "beta", previous=previous)
    (first / "manifest.json").unlink()
    ok, detail = verify_run.check_chain(second, json.loads((second / "manifest.json").read_text()))
    assert ok is False
    assert "gone" in detail


def test_an_unsigned_run_says_so_rather_than_passing(tmp_path):
    """It is not a failed verification; it is a run that never claimed to be verifiable."""
    run = build_run(tmp_path)
    meta = json.loads((run / "signature.json").read_text(encoding="utf-8"))
    meta["algorithm"] = None
    (run / "signature.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    ok, detail = verify_run.check_signature(run, (run / "manifest.json").read_bytes())
    assert ok is False
    assert "unsigned" in detail


def test_a_directory_that_is_not_a_run_is_refused(tmp_path):
    assert verify_run.main([str(tmp_path)]) == 2


@pytest.mark.skipif(not _openssl(), reason="openssl not available")
def test_the_signature_is_actually_checked_and_not_merely_present(tmp_path):
    """Swap in a signature made with a different key: everything is present, nothing is valid."""
    run = build_run(tmp_path)
    other = build_run(tmp_path, "other")
    shutil.copy(other / "manifest.sig", run / "manifest.sig")
    ok, _ = verify_run.check_signature(run, (run / "manifest.json").read_bytes())
    assert ok is False
