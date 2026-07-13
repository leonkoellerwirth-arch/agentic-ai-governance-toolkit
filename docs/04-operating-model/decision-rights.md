# Decision rights

Who may approve what, as a function of the agent's control level. The principle: **authority rises
with control intensity.** A C1 agent should not need a committee; a C4 agent should not go live on
one person's say-so.

> This is a practitioner's toolkit, not legal advice. Calibrate the thresholds to your own risk
> appetite and delegation-of-authority framework.

## Approval authority by control level

| Control level | Go-live approver | Material-change approver | Re-assessment cadence |
|:-------------:|------------------|--------------------------|-----------------------|
| **C1 · Minimal** | Business owner | Business owner | On material change |
| **C2 · Standard** | Business owner + AI team lead | Business owner | At least annually |
| **C3 · Enhanced** | Business owner + Risk (2nd line) sign-off | Business owner + Risk (2nd line) | Quarterly |
| **C4 · Critical** | AI governance board | AI governance board | Quarterly + on any change |

## What counts as a material change

A change is **material** — and re-opens [risk assessment](../02-risk-assessment/agent-risk-model.md)
— when it moves any risk dimension, in particular:

- **Autonomy:** removing or loosening a human-in-the-loop step.
- **Action space:** granting write access, a new integration, or an external effect.
- **Data:** new data categories, especially personal or special-category data.
- **Model:** swapping the underlying model or materially changing prompts/tools.
- **Blast radius:** widening the population or systems the agent can affect.

Everything else (bug fixes, non-behavioural refactors, copy changes) is a **minor change** logged in
the registry without re-assessment.

## Escalation

Any role may **escalate** an agent to the next authority level when in doubt — escalation is never
penalized. Monitoring breaches follow the
[escalation paths](../01-agent-lifecycle/lifecycle-overview.md#escalation-paths); the governance
board is the terminal authority for decisions to continue, restrict, or decommission a C4 agent.

## Reserved decisions

These are never delegated below the AI governance board, regardless of level:

- Approving an exception to a **mandatory control** for the assigned level.
- Approving an agent whose classification is **contested** between 1st and 2nd line.
- Deciding to **keep operating** an agent after a major incident.
