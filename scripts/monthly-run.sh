#!/usr/bin/env bash
# The monthly run — one record per register, with its evidence, signed and chained.
#
#   scripts/monthly-run.sh --registers ../registers --out ../runs --key ~/.keys/rechtsstand.pem
#
# Exit: 0 every register clean · 1 at least one finding · 2 a register could not be produced.
# Meant for a scheduler. A run that fails must be noticed, so 2 is a hard error and not a warning.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT_DIR/.venv/bin/python"; [ -x "$PY" ] || PY="python3"
exec "$PY" "$ROOT_DIR/scripts/monthly_run.py" "$@"
