# BIBLE — agentic-ai-governance-toolkit

The stable mind of this repo: invariants and the decision register. Public-safe (no business
internals). Wins on any in-repo conflict. Change it deliberately, with a commit.

## Zone

Bridge / Tool — real open source, public work sample. Code MIT, documentation CC BY 4.0. Contains
nothing business-internal; all examples are fictional. See `dev/base/CONSTITUTION.md` §1.

## Invariants

_(The rules that must never quietly break. Enforced by `scripts/gate.sh` / the evaluator tests
where possible.)_

- **INV-1 — One rubric, one source.** The scoring rubric lives exactly once, in
  `evaluator/src/agent_evaluator/rubric.yaml`. `risk_score.py` reads it; the doc table in
  `docs/02-risk-assessment/scoring-rubric.md` is rendered from it; a test fails if they drift.
- **INV-2 — No customer internals.** No employer/customer names or recognizable architectures
  (checked in the gate). All example organizations are fictional (e.g. the "Nordbank").
- **INV-3 — Regulatory care.** Article/paragraph references (EU AI Act, DORA, MaRisk) appear only
  where verifiable; otherwise the checklists stay generic. Compliance statements carry a disclaimer.
- **INV-4 — Everything runs.** Every documented command is tested before commit; CI mirrors the
  local gate exactly.

## Decision register

Newest first. Each: date · decision · why · (superseded by …).

- **2026-07-13 — Python project lives under `evaluator/`.** Faithful to the briefing's
  `evaluator/` subproject (own pyproject + README). `scripts/gate.sh` and `.github/workflows/ci.yml`
  are tailored to run the Python surface there instead of at the repo root.
- **2026-07-13 — License replaced GPL-3.0 → dual (MIT + CC BY 4.0).** The repository shipped with a
  GPL-3.0 `LICENSE`; the toolkit is intended as a permissively reusable reference (code MIT) with
  attributable docs (CC BY 4.0). One `LICENSE` file (MIT full text) grants CC BY 4.0 to docs by
  reference, so GitHub cleanly detects MIT.
- **2026-07-13 — Repo onboarded to the `base` paved road.** Backbone scripts, session skills, CI,
  canonical CLAUDE.md/AGENTS.md, security configs.

## Open decisions

_(Blocking questions. Do not start substantive work that depends on an open decision here.)_

- None.
