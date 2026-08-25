#!/usr/bin/env bash
# Verify a monthly run — signature, digests, chain. The command an auditor runs.
#
#   scripts/verify-run.sh ../runs/2026-08/maschinenbau
#
# Exit: 0 verified · 1 something does not hold · 2 not a run directory.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT_DIR/.venv/bin/python"; [ -x "$PY" ] || PY="python3"
exec "$PY" "$ROOT_DIR/scripts/verify_run.py" "$@"
