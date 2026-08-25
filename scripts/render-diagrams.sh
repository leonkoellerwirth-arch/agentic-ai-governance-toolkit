#!/usr/bin/env bash
# Render the Mermaid diagram sources (.mmd) to .svg. The .mmd files are the source of truth; the
# committed .svg files are generated from them by this script. Requires Node/npx (fetches
# @mermaid-js/mermaid-cli on first run) and a Chrome/Chromium for headless rendering.
#
# Set PUPPETEER_EXECUTABLE_PATH to your browser, or rely on the macOS default detected below.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Every docs/**/diagrams directory, so a new area does not silently stop being rendered.
DIAGRAM_DIRS=()
while IFS= read -r d; do DIAGRAM_DIRS+=("$d"); done < <(find "$ROOT_DIR/docs" -type d -name diagrams | sort)

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

count=0
for dir in "${DIAGRAM_DIRS[@]}"; do
  for mmd in "$dir"/*.mmd; do
    [ -e "$mmd" ] || continue
    name="$(basename "$mmd" .mmd)"
    echo "==> ${dir#"$ROOT_DIR"/}/$name.svg"
    npx -y @mermaid-js/mermaid-cli@11 -p "$PUPPET_CFG" -b white \
      -i "$mmd" -o "$dir/$name.svg"
    count=$((count + 1))
  done
done

echo "Done. Rendered $count diagram(s)."
