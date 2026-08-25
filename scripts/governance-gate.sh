#!/usr/bin/env bash
# Governance gate — the evaluator's exit codes turned into one gate, with evidence.
#
# Runs offline and depends on nothing but the evaluator: no GitHub, no network, no CI minutes.
# Use it locally, in a pre-commit hook, in Jenkins/GitLab, or from action.yml — which is a thin
# wrapper around this file, so CI and the local run cannot drift (CONSTITUTION §4).
#
# The run is the evidence. Each requested check writes machine-readable JSON to the evidence
# directory and a readable block to the summary file, both stamped with the evaluator version and
# the commit under test.
#
# Every run also writes manifest.json: which tool, which rulesets (by digest), which commit, when,
# and a SHA-256 per evidence file. That is what a reader needs a year later, and it is deliberately
# beside the results rather than inside them, so nothing consuming the per-check JSON breaks.
#
# Exit: 0 clean · 1 findings · 2 misconfiguration or unusable input.
# Not legal advice — see DISCLAIMER.md.
#
# Usage:
#   scripts/governance-gate.sh --readiness org.yaml
#   scripts/governance-gate.sh --assessment agent.yaml --policy policy.yaml --logs trail.jsonl
#   scripts/governance-gate.sh --readiness org.yaml --no-fail   # report without blocking

# errexit stays off on purpose: this script inspects exit codes itself, and a caller that runs it
# under `bash -e` (GitHub composite steps do) would otherwise kill it on the first finding.
set +e
set -uo pipefail

readiness="" assessment="" logs="" policy=""
evidence="governance-evidence" summary="" fail_on_findings=1

die() { echo "governance-gate: $1" >&2; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --readiness)  readiness="${2:-}"; shift 2 ;;
    --assessment) assessment="${2:-}"; shift 2 ;;
    --logs)       logs="${2:-}"; shift 2 ;;
    --policy)     policy="${2:-}"; shift 2 ;;
    --evidence)   evidence="${2:-}"; shift 2 ;;
    --summary)    summary="${2:-}"; shift 2 ;;
    --no-fail)    fail_on_findings=0; shift ;;
    -h|--help)    sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)            die "unknown argument: $1" ;;
  esac
done

command -v agent-eval >/dev/null 2>&1 || die "agent-eval not on PATH — run ./setup.sh, or pip install ./evaluator"

[ -n "$readiness$assessment$logs" ] || die "no checks requested — pass at least one of --readiness, --assessment, --logs"
[ -z "$assessment" ] || [ -n "$policy" ] || die "--assessment requires --policy"
[ -z "$logs" ]       || [ -n "$policy" ] || die "--logs requires --policy"

mkdir -p "$evidence" || die "cannot create evidence directory: $evidence"
[ -n "$summary" ] || summary="$evidence/summary.md"
: > "$summary" || die "cannot write summary: $summary"

version="$(agent-eval --version)"
commit="$(git rev-parse --short HEAD 2>/dev/null || echo "not a git checkout")"
{
  echo "## Governance Gate"
  echo
  echo "| | |"
  echo "|---|---|"
  echo "| Evaluator | \`$version\` |"
  echo "| Commit | \`$commit\` |"
  echo "| Timestamp (UTC) | $(date -u +%Y-%m-%dT%H:%M:%SZ) |"
  echo
} >> "$summary"

failed=0

# $1 label · $2 evidence basename · rest: agent-eval argv
check() {
  label="$1"; name="$2"; shift 2
  echo "== $label =="
  agent-eval "$@" --json > "$evidence/$name.json" 2> "$evidence/$name.err"
  rc=$?
  # --json prints the report and still exits non-zero on a finding, so the evidence file is
  # complete either way. A failure of the command itself (bad path, invalid input) leaves the
  # JSON empty and a message in .err — that is a gate failure too, never a silent pass.
  if [ "$rc" -eq 0 ]; then
    echo "  ✓ no findings"
    { echo "### ✅ $label"; echo "No findings."; echo; } >> "$summary"
    return 0
  fi

  failed=1
  if [ -s "$evidence/$name.err" ]; then
    sed 's/^/  /' "$evidence/$name.err"
  else
    echo "  ✗ findings — see $evidence/$name.json"
  fi
  {
    echo "### ❌ $label"
    if [ -s "$evidence/$name.json" ]; then
      echo '```json'; head -c 8000 "$evidence/$name.json"; echo; echo '```'
    fi
    if [ -s "$evidence/$name.err" ]; then
      echo '```'; head -c 2000 "$evidence/$name.err"; echo; echo '```'
    fi
    echo
  } >> "$summary"
  return 1
}

[ -z "$readiness" ]  || check "Organizational readiness" readiness \
  readiness --input "$readiness"
[ -z "$assessment" ] || check "Policy check" policy-check \
  policy-check --input "$assessment" --policy "$policy"
[ -z "$logs" ]       || check "Audit-log thresholds" log-analyze \
  log-analyze --input "$logs" --policy "$policy"

# The manifest is what makes the directory archivable: tool, ruleset fingerprint, commit, and a
# digest per file. Written last, so it covers everything the run produced.
if agent-eval manifest --evidence "$evidence" --commit "$commit" >/dev/null 2>&1; then
  echo "manifest: $evidence/manifest.json"
else
  echo "governance-gate: could not write the evidence manifest" >&2
  failed=1
fi

echo "evidence: $evidence  ·  summary: $summary"

if [ "$failed" -eq 0 ]; then
  echo "GOVERNANCE GATE: PASS"
  exit 0
fi

echo "GOVERNANCE GATE: FAIL"
if [ "$fail_on_findings" -eq 0 ]; then
  echo "(--no-fail: reporting only, not blocking)"
  exit 0
fi
exit 1
