# Scoring rubric — from dimensions to control intensity

This rubric turns the six [risk-model](agent-risk-model.md) scores into a **control-intensity level**
(C1–C4) and the minimum controls that level demands.

> This is a practitioner's toolkit, not legal advice. Treat the control lists as a floor to adapt to
> your own policies, not as a compliance guarantee.

## Single source of truth

The rubric below is generated from `evaluator/src/agent_evaluator/rubric.yaml`. The evaluator scores
against the same file, and a test (`evaluator/tests/test_rubric_consistency.py`) fails if this
document and the YAML ever diverge. To change the rubric, edit the YAML and run:

```bash
agent-eval render-docs      # rewrites the generated tables in this folder
```

## Aggregation

Each of the six dimensions is scored 1–5 and the scores are **summed** (equal weight), giving a total
between 6 and 30. The total falls into one band:

<!-- GENERATED:bands START (source: evaluator/src/agent_evaluator/rubric.yaml — regenerate with: agent-eval render-docs) -->
| Level | Name | Total score | What it means |
|:-----:|------|:-----------:|---------------|
| C1 | Minimal | 6–10 | Light-touch. Standard engineering controls are enough. |
| C2 | Standard | 11–16 | Documented controls, an accountable owner, periodic review. |
| C3 | Enhanced | 17–22 | Human-in-the-loop, active monitoring, frequent re-assessment. |
| C4 | Critical | 23–30 | Per-action authorization, continuous oversight, board visibility. |
<!-- GENERATED:bands END -->

## Overrides — when one dimension decides

Some risks are categorical. An agent that can move money externally, cause irreversible external
effects, or touch special-category data needs enhanced control **even if its total is modest**. These
overrides raise the floor; they never lower it. The final level is the higher of the banded total and
any triggered override.

<!-- GENERATED:overrides START (source: evaluator/src/agent_evaluator/rubric.yaml — regenerate with: agent-eval render-docs) -->
| Dimension | Condition | Raises floor to | Why |
|-----------|:---------:|:---------------:|-----|
| Action space | ≥ 5 | C4 | Acting on the outside world (payments, irreversible orders) is never light-touch. |
| Reversibility | ≥ 5 | C3 | Irreversible external effects require a human in the loop at minimum. |
| Data sensitivity | ≥ 5 | C3 | Special-category data or secrets require enhanced controls at minimum. |
<!-- GENERATED:overrides END -->

## Minimum controls per level

Each level includes the intent of the levels below it; only the additive minimums are listed. Adapt
them to your own control catalogue — these are a floor, not a ceiling.

<!-- GENERATED:controls START (source: evaluator/src/agent_evaluator/rubric.yaml — regenerate with: agent-eval render-docs) -->
#### C1 — Minimal (score 6–10)

- Owner recorded in the agent registry.
- Standard logging; errors surfaced to the owning team.
- Re-assess on any material change.

#### C2 — Standard (score 11–16)

- Documented use-case intake and risk assessment on file.
- A named accountable owner signs off before go-live.
- Operational KPIs monitored; re-assessment at least annually.

#### C3 — Enhanced (score 17–22)

- Human-in-the-loop for in-scope actions (explicit approve/reject).
- Daily log review against thresholds, with alerting on breaches.
- Independent (2nd-line) review before go-live; re-assessment quarterly.
- Documented rollback and kill-switch procedure.

#### C4 — Critical (score 23–30)

- Per-action pre-authorization by an accountable human.
- Continuous monitoring with real-time alerting and a tamper-evident audit trail.
- 2nd-line and, where relevant, 3rd-line review; re-assessment at least quarterly.
- Tested kill-switch and incident runbook; visibility at the governance board.
<!-- GENERATED:controls END -->

## Worked examples

Three fictional use cases are scored end to end in [`examples/`](examples/), including one where an
override lifts an otherwise-Enhanced agent to Critical.
