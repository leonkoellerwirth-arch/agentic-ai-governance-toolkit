#!/usr/bin/env bash
# Does a newer consolidated version of a pinned act exist?
#
# The source lock pins a consolidated text, which is what makes a citation checkable — and also
# what lets the register go quietly stale, because a pin never notices that the law moved. This
# asks the Publications Office directly.
#
# Exit: 0 the pins are current · 1 a newer consolidation exists · 2 the endpoint could not be reached.
# Run it on a schedule. A finding here is the earliest possible warning that filed control mappings
# have started to rot.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT_DIR/.venv/bin/python"; [ -x "$PY" ] || PY="python3"
exec "$PY" "$ROOT_DIR/scripts/check_consolidations.py" "$@"
