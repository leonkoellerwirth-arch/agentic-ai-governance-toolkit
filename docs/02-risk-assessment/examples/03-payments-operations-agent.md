# Worked example 3 — Payments operations agent (C4 by override)

**Fictional use case.** *Nordbank* deploys an agent that prepares and initiates outbound supplier
payments from operational queues. It acts within a defined scope, with staff reviewing exceptions.

Reproduce this with the evaluator:

```bash
agent-eval score --input evaluator/examples/usecase-03-payments-operations-agent.yaml
```

## Scores

| Dimension | Score | Why |
|-----------|:-----:|-----|
| Autonomy | 3 | Acts within scope; humans review exceptions. |
| Action space | **5** | Initiates external payments — acts on the outside world. |
| Reversibility | 4 | A released payment is largely irreversible. |
| Data sensitivity | 3 | Payment and counterparty data. |
| Explainability | 3 | Model-driven; each step logged. |
| Blast radius | 3 | Affects a critical business function. |

**Total: 21 → C3 (Enhanced) by score, raised to C4 (Critical) by override.**

The total of 21 sits in the Enhanced band. But `action_space = 5` triggers the override *"acting on
the outside world is never light-touch"*, which raises the floor to **C4**. The final level is the
higher of the two.

## What C4 requires

- Per-action pre-authorization by an accountable human.
- Continuous monitoring with real-time alerting and a tamper-evident audit trail.
- 2nd-line and, where relevant, 3rd-line review; re-assessment at least quarterly.
- Tested kill-switch and incident runbook; visibility at the governance board.

## Reading

This is the case the override exists for. Judged purely on its aggregate, the agent looks like a
peer of the customer-servicing agent in example 2 — both total in the high teens to low twenties. But
one of them can move money out of the bank, and that is a categorical difference, not an incremental
one. A purely additive score would let a low autonomy or a low blast-radius "average away" the
severity of an irreversible external action. The override refuses that trade: if the agent can pay a
counterparty, per-action authorization is the floor, whatever the other five dimensions say.
