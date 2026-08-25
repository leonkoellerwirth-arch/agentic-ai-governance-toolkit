# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] — 2026-08-25

### Fixed

- **The gate ignored `fail-on-findings` and died on the first finding.** GitHub runs composite
  `run:` steps under `bash -e`; the script set `-uo pipefail` but never disabled errexit, so the
  first check that exited non-zero killed it before the flag was consulted — and before the
  remaining checks ran, so the evidence was incomplete too. `set +e` is now explicit, with the
  reason in a comment above it.

  Found by `governance-gate-selftest.yml` on the first run after release, which is the entire
  argument for asserting on the `passed` output rather than on job colour: the job it was
  supposedly testing had failed, and only the assertion said why. The local test harness now
  invokes the script the way the runner does (`bash --noprofile --norc -eo pipefail`), because
  a harness that is more forgiving than production tests nothing.

  `v0.2.0` carries the action but should not be pinned.

## [0.2.0] — 2026-08-25

### Added

- **Scope statement** ([`docs/00-scope/regulatory-scope.md`](docs/00-scope/regulatory-scope.md)):
  what this toolkit maps, what it deliberately does not, and why the three repositories answer that
  differently. Three questions that look alike — what an article requires (mapped), whether it
  applies to a given system (not mapped), how well an organization meets it (not scored) — with the
  reasoning for each boundary and where triage sits between the first two.

  This closes a gap that was visible from outside and not from inside: this toolkit maps the EU AI
  Act, `rag-approval-blueprint` declines to, and `platform-decision-kit` carries no regulatory
  checklist at all. Each position is sound on its own; read side by side and unexplained, they read
  as inconsistency. Linked from the README and `DISCLAIMER.md`. The document cites no article
  numbers of its own and points at the checklists instead, per the rule the reference checker
  already enforces on prose.

- **Governance gate as a composite action** (`action.yml`): the evaluator's exit codes were already
  a gate — `readiness`, `policy-check` and `log-analyze` each exit non-zero on a finding — but every
  consuming repository had to install the toolkit and know the CLI to use them. It now references
  the action instead, pinned to a tag, and the rubric travels with it rather than being copied.

  **The run is the evidence.** Each check writes machine-readable JSON to `governance-evidence/`,
  uploaded as a build artifact, and a readable block to the job summary — both stamped with the
  evaluator version, the commit under test and the run id. A reviewer reads the summary, an auditor
  reads the JSON, and neither depends on a screenshot. `fail-on-findings: "false"` reports without
  blocking, for a first rollout on a repository that has never been gated.

  Checks are opt-in per input and at least one is required; a misconfiguration (an `assessment`
  without a `policy`, or no check at all) exits 2 rather than degrading into a silent pass — as does
  an unreadable input file. `.github/workflows/governance-gate-selftest.yml` asserts all three
  directions on the action's `passed` output rather than on job colour, because a gate that never
  blocks is a green check that means nothing. The clean-input case is built in the runner and
  discarded with it; every committed example is a realistic negative case on purpose.

- **Agent readiness rubric** (INV-7): `evaluator/src/agent_evaluator/readiness.yaml` and the new
  `agent-eval readiness` command answer the half of the question the toolkit could not answer
  before. `rubric.yaml` scores what an agent can do to you; `readiness.yaml` scores whether the
  organization running it has the control that implies. Six dimensions (inventory, oversight,
  traceability, containment, assurance, currency), each scored R0–R3 against falsifiable anchors and
  each derived from a demand the toolkit already makes elsewhere. Rendered to
  [`docs/06-readiness/agent-readiness-rubric.md`](docs/06-readiness/agent-readiness-rubric.md);
  `evaluator/examples/org-readiness-demo.yaml` is a runnable fictional organization whose control
  levels are computed by `agent-eval score`, not asserted, so the two rubrics cannot drift apart.

  Readiness is measured **relative to the exposure actually in production**, never absolutely.
  Aggregation is a deliberately non-compensatory minimum — the requirement is the highest any agent
  triggers, the achieved level the lowest reached by an agent that triggers it — and **no 0–100
  index is produced**, because a single number invites optimizing the number instead of the control.
  Ten further entries in the policy-decision register cover every threshold the rubric introduces,
  including why `assurance` deliberately stays at R1 for C2 and why `traceability` is the one place
  readiness demands more than exposure does.
- **Regulatory source lock** (INV-5): `evaluator/src/agent_evaluator/regulatory_sources.yaml` pins
  every article the checklists cite to an act, a CELEX id, an Official Journal citation, and the
  consolidated version it was last checked against — with the EUR-Lex URLs of that check. Each
  checklist now carries a generated source-lock header, and
  [`docs/03-checklists/regulatory-sources.md`](docs/03-checklists/regulatory-sources.md) renders the
  full registry. `test_regulatory_sources.py` fails if a checklist cites an article the lock does
  not carry, or if the lock carries one no checklist cites. The lock records **which text applies**
  — never deadlines, penalties, or what an obligation requires.
- **Policy-decision register** (INV-6): `evaluator/src/agent_evaluator/policy_decisions.yaml` records
  every threshold that is a judgement call rather than a derivation — the reasoning, the external
  support where any exists, and **what the choice accepts as a cost**. Rendered to
  [`docs/02-risk-assessment/policy-decisions.md`](docs/02-risk-assessment/policy-decisions.md). The
  thresholds needing cover are computed from `rubric.yaml`, so a new band or override cannot land
  without its decision, and `test_policy_decisions.py` fails either way round.
- **Incident response** (docs/05): sector-independent handling for agent incidents — what counts as
  one, severity by control level, a five-step runbook, stop/rollback expectations per level, and the
  scenarios worth rehearsing. Previously this existed only in the DORA checklist, which binds
  defined financial entities.
- **Provider and model dependency** (docs/04): what to record per agent, concentration at the
  organization level, the three ways a provider changes underneath you, and exit expectations by
  control level. Also previously DORA-only.
- **Incident section in the EU AI Act checklist** (EN + DE): serious-incident definition and
  reporting paths, post-market monitoring feeding re-assessment, and provider-change triggers.

- Pre-rendered `.svg` versions of the three lifecycle diagrams, plus `scripts/render-diagrams.sh`
  to regenerate them from the `.mmd` sources.
- **Governance console** (`app/`): a static Vite/React surface for the risk assessment. It reads the
  same `rubric.yaml` as the evaluator (INV-1), walks the dimensions interactively, and shows the
  resulting risk class. Built and linted in the gate alongside the Python surface.

### Changed

- Every identifier in the logging examples now carries a `DEMO-` prefix, and the convention is
  stated where the example lives. A log line is the most copied artifact in a governance document;
  `"actor": "human:clerk-014"` read as a real personnel number and got reused as one.

## [0.1.0] — 2026-07-13

First public release.

### Added

- **Agent lifecycle** (docs/01): seven phases with goal, input/output, responsible role, and control
  point each, plus Mermaid diagrams (swimlane lifecycle, triage flow, escalation paths).
- **Risk model** (docs/02): six scoring dimensions (1–5) aggregating to control intensity C1–C4,
  with categorical overrides and minimum controls — defined once in `rubric.yaml` and rendered into
  the docs, with a consistency test. Three fictional worked examples.
- **Checklists** (docs/03): EU AI Act and DORA checklists for agents in English and German, plus a
  go-live readiness gate. Regulatory references are marked "verify" and carry a not-legal-advice note.
- **Operating model** (docs/04): roles & RACI, decision rights by control level, committee templates.
- **Monitoring** (docs/05): KPI catalog and audit-trail logging requirements.
- **Evaluator** (evaluator/): a Python CLI/library — `score`, `policy-check`, `log-analyze`, and an
  optional local LLM `judge` — with an offline test suite.
- **Templates**: use-case intake, agent registry entry, decommissioning protocol.
- Paved-road tooling: hard gate, CI across Python 3.11–3.13, security scanning, dual license
  (MIT for code, CC BY 4.0 for documentation).

[Unreleased]: https://github.com/leonkoellerwirth-arch/agentic-ai-governance-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/leonkoellerwirth-arch/agentic-ai-governance-toolkit/releases/tag/v0.1.0
