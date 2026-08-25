#!/usr/bin/env bash
# Refresh evaluator/src/agent_evaluator/official_headings.json from the primary text.
#
# The headings come from the Publications Office Cellar repository, which is the official machine
# interface to the same text EUR-Lex renders. The EUR-Lex web pages answer automated requests with
# HTTP 202 and an empty body, so anything scraping them is reading a challenge page, not the law.
#
#   http://publications.europa.eu/resource/celex/{CELEX}
#   Accept: application/xhtml+xml
#   Accept-Language: eng
#
# This needs the network and is therefore a script, not a test — the gate stays offline. The gate
# checks the register against the committed snapshot; this is what moves the snapshot, and moving
# it is a deliberate act with a diff someone reads.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT_DIR/evaluator/src/agent_evaluator/official_headings.json"
UA="Mozilla/5.0 (compatible; agentic-ai-governance-toolkit reference check)"

command -v curl >/dev/null 2>&1 || { echo "curl is required" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fetch() {
  local celex="$1"
  echo "==> $celex"
  curl -sSL -A "$UA" --max-time 120 \
    -H "Accept: application/xhtml+xml" -H "Accept-Language: eng" \
    "http://publications.europa.eu/resource/celex/$celex" -o "$tmp/$celex.xhtml"
  local size
  size=$(wc -c < "$tmp/$celex.xhtml" | tr -d ' ')
  # A challenge page or an error notice is far smaller than a regulation.
  [ "$size" -gt 100000 ] || { echo "✗ $celex came back as $size bytes — not the full text" >&2; exit 1; }
}

fetch 02024R1689-20260727
fetch 32022R2554

python3 "$ROOT_DIR/scripts/extract_headings.py" "$tmp" "$OUT"
echo "✓ wrote ${OUT#"$ROOT_DIR"/}"
echo "  Review the diff before committing: a moved heading is a change in the law, not a refresh."
