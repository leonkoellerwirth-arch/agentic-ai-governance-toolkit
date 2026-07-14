# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Pre-rendered `.svg` versions of the three lifecycle diagrams, plus `scripts/render-diagrams.sh`
  to regenerate them from the `.mmd` sources.

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
