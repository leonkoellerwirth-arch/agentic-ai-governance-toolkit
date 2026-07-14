#!/usr/bin/env bash
# Render the Mermaid diagram sources (.mmd) to .svg. The .mmd files are the source of truth; the
# committed .svg files are generated from them by this script. Requires Node/npx (fetches
# @mermaid-js/mermaid-cli on first run) and a Chrome/Chromium for headless rendering.
#
# Set PUPPETEER_EXECUTABLE_PATH to your browser, or rely on the macOS default detected below.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIAGRAMS="$ROOT_DIR/docs/01-agent-lifecycle/diagrams"

command -v npx >/dev/null 2>&1 || { echo "npx (Node.js) is required" >&2; exit 1; }

# Find a browser for Puppeteer if the caller did not supply one.
if [ -z "${PUPPETEER_EXECUTABLE_PATH:-}" ]; then
  for candidate in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "$(command -v google-chrome 2>/dev/null || true)" \
    "$(command -v chromium 2>/dev/null || true)"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
      PUPPETEER_EXECUTABLE_PATH="$candidate"; break
    fi
  done
fi
export PUPPETEER_EXECUTABLE_PATH PUPPETEER_SKIP_DOWNLOAD=1

PUPPET_CFG="$(mktemp)"
trap 'rm -f "$PUPPET_CFG"' EXIT
printf '{"args":["--no-sandbox"]}' > "$PUPPET_CFG"

for mmd in "$DIAGRAMS"/*.mmd; do
  name="$(basename "$mmd" .mmd)"
  echo "==> $name.svg"
  npx -y @mermaid-js/mermaid-cli@11 -p "$PUPPET_CFG" -b white \
    -i "$mmd" -o "$DIAGRAMS/$name.svg"
done

echo "Done. Rendered $(find "$DIAGRAMS" -name '*.svg' | wc -l | tr -d ' ') diagram(s)."
