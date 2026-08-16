# BIBLE — agentic-ai-governance-toolkit

The stable mind of this repo: invariants and the decision register. Public-safe (no business
internals). Wins on any in-repo conflict. Change it deliberately, with a commit.

## Zone

Bridge / Tool — real open source, public work sample. Code MIT, documentation CC BY 4.0. Contains
nothing business-internal; all examples are fictional. See `dev/base/CONSTITUTION.md` §1.

## Invariants

_(The rules that must never quietly break. Enforced by `scripts/gate.sh` / the evaluator tests
where possible.)_

- **INV-1 — One rubric, one source.** Each rubric lives exactly once. The exposure rubric is
  `evaluator/src/agent_evaluator/rubric.yaml` (`risk_score.py` reads it; the doc table in
  `docs/02-risk-assessment/scoring-rubric.md` is rendered from it); the readiness rubric is
  `readiness.yaml` (`readiness.py` reads it; `docs/06-readiness/agent-readiness-rubric.md` is
  rendered from it). A test fails if either drifts from its documentation.
- **INV-2 — No customer internals.** No employer/customer names or recognizable architectures
  (checked in the gate). All example organizations are fictional (e.g. the "Nordbank").
- **INV-3 — Regulatory care.** Article/paragraph references (EU AI Act, DORA, MaRisk) appear only
  where verifiable; otherwise the checklists stay generic. Compliance statements carry a disclaimer.
- **INV-4 — Everything runs.** Every documented command is tested before commit; CI mirrors the
  local gate exactly.
- **INV-5 — Every regulatory reference is pinned to a version.** Article references live exactly
  once, in `evaluator/src/agent_evaluator/regulatory_sources.yaml`, with CELEX id, Official Journal
  citation, the consolidated version checked, and the EUR-Lex URL of that check. The checklist
  headers and `docs/03-checklists/regulatory-sources.md` are rendered from it;
  `test_regulatory_sources.py` fails in both directions (cited-but-unpinned, pinned-but-uncited).
  The lock records **provenance only** — never deadlines, penalties, or what an obligation
  requires. Commentary, news, and AI-generated review are never the source of an entry.
- **INV-6 — Every threshold is derived or decided.** A number in a rubric is either traceable to a
  demand the toolkit already makes (recorded in the rubric) or a judgement call recorded in
  `evaluator/src/agent_evaluator/policy_decisions.yaml` with its rationale, its external support if
  any, and **what it accepts as a cost**. Nothing may be neither. The thresholds needing cover are
  computed from the rubric files, so a new band or override cannot land without its decision, and a
  decision cannot outlive the threshold it justifies.
- **INV-7 — Readiness is relative to exposure, never absolute.** The readiness rubric may never
  demand more than the exposure rubric already demands; every dimension records the demand it is
  derived from, and `required` never falls as the control level rises. The demo organization's
  control levels are **computed** by `score_agent`, not asserted, so the two rubrics cannot disagree
  in the one place a reader compares them. No single index value is produced — a required/achieved
  pair per dimension cannot be quoted without its exposure, and a number invites optimizing the
  number instead of the control. Enforced by `test_readiness_consistency.py` and
  `test_readiness_score.py`.

## Decision register

Newest first. Each: date · decision · why · (superseded by …).

- **2026-08-16 — The readiness rubric enters the source tree (INV-7).** The toolkit could say how
  much control an agent needs and could not say whether the organization has it — the half of the
  question every real conversation is actually about. `readiness.yaml` closes that, with ten new
  policy decisions, because the INV-6 check computed its thresholds the moment the file existed and
  refused to pass without them. Three choices are worth naming: aggregation is a **non-compensatory
  minimum**, recorded as a chosen decision rule and not as methodical correctness; **no 0–100 index**
  is produced, which costs adoption on purpose; and `traceability` is the single place the readiness
  rubric demands slightly more than the exposure rubric (R3 already at C3), justified by asymmetry of
  repair — every other gap can be closed going forward, a decision that was never traceable cannot.
  `PD-ASSURANCE-001` goes the other way and keeps `assurance` at R1 for C2 rather than tightening a
  number the C2 control list does not carry: if C2 should demand independent review, the correction
  belongs in `rubric.yaml`, where everything downstream would follow. Two things are said out loud
  rather than left to be discovered: **the gaming path** — retiring the single riskiest agent lowers
  every reported figure without a control improving, and the result names that agent when one sets
  the exposure alone — and **"the evaluator proves provenance, not truth"**, which bounds what a
  deterministic tool can demonstrate at all. A reproducible result is not a correct rubric.
- **2026-08-14 — Thresholds get a decision register (INV-6).** The README already said the
  thresholds are "a starting point, not a calibrated standard" — honest, but useless to someone
  defending a control level in a review. The register is the long version: which numbers are
  judgement, the reasoning, and what each choice gets wrong on purpose. The band boundaries
  (10/16/22) are named in it as the least defensible number in the rubric, because saying so first
  is cheaper than being asked. Support from outside the project is recorded where it exists and left
  empty where it does not — an invented citation is worse than an admitted judgement call.
- **2026-08-14 — Regulatory references get a source lock (INV-5).** The toolkit shipped 44 article
  references, each marked "verify", none naming the version it was written against — and the AI Act
  was amended by Regulation (EU) 2026/1744 (in force 2026-07-27) after they were written. "Verify"
  without "verify against what" puts the burden on the reader and keeps none. The lock is a
  retrofit of what is already published, and the first consumer of the same pattern the readiness
  work will need. It deliberately carries no dates, deadlines, or obligations: recording provenance
  is not legal advice, and stating what an obligation requires would be.
- **2026-07-14 — Ship pre-rendered SVGs for the diagrams.** `scripts/render-diagrams.sh` renders the
  `.mmd` sources to committed `.svg` via mermaid-cli + a local Chrome. The `.mmd` files remain the
  source of truth; the overview embeds Mermaid for native GitHub rendering and links the SVGs for use
  elsewhere. Supersedes the 2026-07-13 "no pre-rendered SVGs" decision (tooling turned out available).
- **2026-07-13 — Released v0.1.0.** First public version, all seven milestones built and
  CI-green. Signed wheel/sdist + SBOM via the release workflow. Known limitations named in the
  README (reference pattern, not legal advice, illustrative rubric, evaluator not a product).
- **2026-07-13 — Dependabot removed.** Owner preference (unwanted PRs/notifications). Supply-chain
  safety stays in CI via pip-audit + gitleaks, which open no PRs.
- **2026-07-13 — Diagrams ship as embedded Mermaid + `.mmd` sources, no pre-rendered SVGs.** GitHub
  renders Mermaid natively (briefing §4.1); SVG tooling was not available and would add stale blobs.
  _(Superseded 2026-07-14 — SVGs are now rendered and committed.)_
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
