# agent-evaluator

A small, readable Python tool that operationalizes the governance artifacts in this repository:
it scores an agent use case against the risk rubric, checks an agent against a machine-readable
policy, and flags runtime logs against operational thresholds.

> Reference pattern, not a framework. Not legal advice. The core runs with no LLM and no network;
> the optional `llm_judge` demonstrates an evaluator-agent pattern locally via Ollama.

## Quickstart

```bash
./setup.sh   # from the repo root: .venv + install + offline tests
source .venv/bin/activate

# 1. Score a use case → risk total, control level, required controls
agent-eval score --input evaluator/examples/usecase-03-payments-operations-agent.yaml

# 2. Check an agent against a machine-readable policy (exit 1 on any violation)
agent-eval policy-check \
  --input evaluator/examples/agent-for-policy-check.yaml \
  --policy evaluator/policies/example-policy.yaml

# 3. Analyze an agent's audit trail against policy thresholds (exit 1 on any finding)
agent-eval log-analyze \
  --input evaluator/examples/logs-sample.jsonl \
  --policy evaluator/policies/example-policy.yaml
```

Add `--json` to `score`, `policy-check`, and `log-analyze` for machine-readable output.
`agent-eval render-docs` regenerates the rubric tables in `docs/` from `rubric.yaml`.

The optional `judge` command (`agent-eval judge`) demonstrates the local LLM-as-judge pattern and
requires the `llm` extra plus a running Ollama; it is a reference pattern, not a production system.

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
