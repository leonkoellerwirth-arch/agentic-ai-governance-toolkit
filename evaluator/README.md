# agent-evaluator

A small, readable Python tool that operationalizes the governance artifacts in this repository:
it scores an agent use case against the risk rubric, checks an agent against a machine-readable
policy, and flags runtime logs against operational thresholds.

> Reference pattern, not a framework. Not legal advice. The core runs with no LLM and no network;
> the optional `llm_judge` demonstrates an evaluator-agent pattern locally via Ollama.

## Quickstart

```bash
cd evaluator
../setup.sh              # or: python3.11 -m venv .venv && .venv/bin/pip install -e ".[dev]"
agent-eval --version
agent-eval info
```

The `score`, `policy-check`, and `log-analyze` subcommands are wired in milestones M2 and M6.

## Architecture

```
src/agent_evaluator/
  risk_score.py     control-intensity scoring — reads the single-source rubric.yaml
  policy_check.py   rule-based checks against a YAML policy
  log_analyzer.py   thresholds over a JSONL audit trail
  llm_judge.py      OPTIONAL: local LLM-as-judge pattern (Ollama), isolated behind an extra
  rubric.yaml       the ONE source of truth for the scoring rubric (docs + code read from it)
policies/           example machine-readable policy
examples/           example use-case inputs for `agent-eval score`
tests/              offline pytest suite; real-model tests are @slow
```

The scoring rubric exists exactly once — in `rubric.yaml`. The documentation table in
`docs/02-risk-assessment/scoring-rubric.md` is rendered from it, and a test fails if the two drift.
