# Roles and RACI

Who does what across the [agent lifecycle](../01-agent-lifecycle/lifecycle-overview.md). The model
uses the three lines of defense plus the roles an agent programme actually needs day to day.

> This is a practitioner's toolkit, not legal advice. Map these roles onto your own organization —
> the names matter less than the separation: whoever builds the agent does not also sign off its risk.

## Roles

| Role | Line | What they own |
|------|------|---------------|
| **Business owner** | 1st | The use case, its value, and its residual risk. Accountable for the agent in production. |
| **AI team / Engineering** | 1st | Designing, building, validating, and running the agent and its controls. |
| **Risk & Compliance** | 2nd | Independent risk assessment, the control framework, sign-off at higher levels. |
| **Data protection / Security** | 2nd | Personal-data handling, security of the action space and data flows. |
| **Internal audit** | 3rd | Independent assurance that the governance actually works as designed. |
| **AI governance board** | — | Cross-functional body that owns the framework and decides on high-risk agents (see [committee templates](committee-templates.md)). |
| **IT operations** | 1st | Running, monitoring, and retiring the agent as an ICT asset. |

## RACI across the lifecycle

R = Responsible (does the work) · A = Accountable (one per row) · C = Consulted · I = Informed.

| Lifecycle phase | Business owner | AI team | Risk & Compliance | IT operations | Gov. board |
|-----------------|:-------------:|:-------:|:-----------------:|:-------------:|:----------:|
| 1 · Intake & Triage | **A** | R | C | I | I |
| 2 · Risk Assessment | C | C | **A/R** | I | I (C4: C) |
| 3 · Design & Controls | I | **A/R** | C | C | — |
| 4 · Validation | I | **A/R** | C (C3+: R) | C | — |
| 5 · Go-Live | **A** | R | C (C3+: approves) | C | Approves (C4) |
| 6 · Operate & Monitor | A | R | C | **R** | I |
| 7 · Change & Decommissioning | A | R | C | **R** | I (C4: C) |

Notes:

- **One accountable role per phase.** Where the table shows A on two roles (phase 2), it means the
  same function is both accountable and doing the work — risk assessment is owned end to end by the
  2nd line, by design, to keep it independent of the builders.
- **The level raises involvement.** At **C3–C4**, Risk & Compliance moves from Consulted to an
  approver, and C4 agents additionally go to the governance board for go-live and for any material
  change. See [decision rights](decision-rights.md).
- **Audit (3rd line) sits outside the flow.** It provides periodic independent assurance over the
  whole programme rather than signing off individual agents.
