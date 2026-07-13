# Worked example 1 — Internal knowledge assistant (C1)

**Fictional use case.** *Nordbank*, a fictional regional bank, deploys an assistant that answers
staff questions about internal policies by retrieving and summarizing approved documents. It is
read-only: an employee reads the answer and decides what to do. No customer data, no writes.

Reproduce this with the evaluator:

```bash
agent-eval score --input evaluator/examples/usecase-01-internal-knowledge-assistant.yaml
```

## Scores

| Dimension | Score | Why |
|-----------|:-----:|-----|
| Autonomy | 1 | Proposes answers; the employee acts. |
| Action space | 1 | Read-only retrieval and summarization. |
| Reversibility | 1 | Produces text only; nothing to undo. |
| Data sensitivity | 2 | Internal, non-personal policy documents. |
| Explainability | 3 | Model-driven, but every answer and its sources are logged. |
| Blast radius | 2 | Affects the individual employee's task. |

**Total: 10 → C1 (Minimal).** No override triggers.

## What C1 requires

- Owner recorded in the agent registry.
- Standard logging; errors surfaced to the owning team.
- Re-assess on any material change.

## Reading

The only score above the floor is explainability (3): the assistant is an LLM, so answers are not
deterministic. That is contained by logging every answer with its sources — the trace exists even
though the generation does not repeat. Nothing the agent does reaches a customer or changes a system,
so light-touch control is proportionate. The moment this assistant is allowed to *act* on an
answer — open a ticket, change a record — its action space and reversibility rise and it leaves C1.
