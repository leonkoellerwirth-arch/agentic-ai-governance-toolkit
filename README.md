# agentic-ai-governance-toolkit

[![CI](https://github.com/leonkoellerwirth-arch/agentic-ai-governance-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/leonkoellerwirth-arch/agentic-ai-governance-toolkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/code-MIT-yellow.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/badge/lint-ruff-261230.svg)](https://github.com/astral-sh/ruff)

**Practical governance artifacts for AI agents in regulated organizations — lifecycle models, risk
scoring, EU AI Act & DORA checklists, and a working evaluator.**

Governance frameworks stay abstract; agents need operationalized controls. This repository puts the
tools on the table: a seven-phase agent lifecycle, a six-dimension risk model that maps to control
intensity, checklists in English and German, an operating model, monitoring requirements, and a
small Python evaluator that scores a use case and names the controls it demands.

> A reference pattern, not a framework. Distilled from practice in regulated environments. This is a
> practitioner's toolkit, **not legal advice** — see [`DISCLAIMER.md`](DISCLAIMER.md).

---

## Status

First public build, assembled in milestones (M1–M7). The full README — overview diagram, quickstart,
and the linked table of contents — lands in M7. Every commit passes the same hard gate CI runs
(`./scripts/gate.sh`): lint, format, offline tests, and the governance guardrails.

## Layout

```
docs/01-agent-lifecycle/    seven-phase lifecycle + Mermaid diagrams
docs/02-risk-assessment/    risk model, scoring rubric, worked examples
docs/03-checklists/         EU AI Act & DORA checklists (EN/DE), go-live gates
docs/04-operating-model/    roles & RACI, decision rights, committee templates
docs/05-monitoring/         KPI catalog, logging requirements
evaluator/                  Python: risk scoring, policy checks, log analysis, optional LLM judge
templates/                  intake, agent registry, decommissioning
```

## License

Dual-licensed: source code under the **MIT License**, documentation and artifacts under
**CC BY 4.0**. See [`LICENSE`](LICENSE).

## Who is behind this

Leon Köllerwirth Hlihel — Interim IT leader & principal consultant for AI governance and agentic AI
operating models, enterprise architecture in regulated environments (BaFin/DORA).
Website: [leonkoellerwirth.de](https://leonkoellerwirth.de).
