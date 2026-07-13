# Worked example 2 — Customer-servicing agent (C3)

**Fictional use case.** *Nordbank* deploys an agent that resolves routine servicing requests —
address changes, standing-order edits — by updating the CRM system of record within a pre-approved
scope. Staff spot-check a sample of the agent's actions rather than every one.

Reproduce this with the evaluator:

```bash
agent-eval score --input evaluator/examples/usecase-02-customer-servicing-agent.yaml
```

## Scores

| Dimension | Score | Why |
|-----------|:-----:|-----|
| Autonomy | 3 | Acts within a narrow, pre-approved scope; humans spot-check. |
| Action space | 3 | Writes to the CRM system of record. |
| Reversibility | 3 | Corrections need a manual, tracked process. |
| Data sensitivity | 3 | Personal customer data (GDPR-relevant). |
| Explainability | 3 | Model-driven; each step logged and attributable. |
| Blast radius | 3 | Affects a defined customer segment. |

**Total: 18 → C3 (Enhanced).** No override triggers; the total alone lands in Enhanced.

## What C3 requires

- Human-in-the-loop for in-scope actions (explicit approve/reject).
- Daily log review against thresholds, with alerting on breaches.
- Independent (2nd-line) review before go-live; re-assessment quarterly.
- Documented rollback and kill-switch procedure.

## Reading

Nothing here is extreme, but nothing is trivial either: the agent writes real customer records, on
its own, in a system of record, touching personal data. Six "middle" scores compound into Enhanced
control. The practical consequence is the human-in-the-loop requirement: spot-checking a sample is
not enough at C3 — in-scope actions need an explicit approve/reject step, or the scope must be
narrowed until the residual risk fits C2. This is the most common place for an agent programme to
under-invest, because no single dimension looks alarming on its own.
