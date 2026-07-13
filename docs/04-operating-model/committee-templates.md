# AI governance board — templates

The AI governance board owns the control framework and decides on the agents that need the most
oversight. These templates make its meetings short and its decisions traceable.

> This is a practitioner's toolkit, not legal advice. Adapt membership and cadence to your
> organization; the point is a standing, minuted body with clear decision rights.

## Charter (one page)

- **Purpose:** own the agent governance framework; decide on C4 (and contested C3) agents; oversee
  the agent portfolio's aggregate risk.
- **Cadence:** monthly, plus on-demand for a major incident.
- **Membership:** Risk & Compliance (chair), AI/Engineering lead, Business representation, Data
  protection/Security, IT operations. Internal audit attends as an observer.
- **Quorum:** chair + at least three other functions, including AI/Engineering and a business
  representative.
- **Decision rights:** see [decision rights](decision-rights.md).

## Standing agenda

| # | Item | Owner | Time |
|:-:|------|-------|:----:|
| 1 | Approve previous minutes and open actions | Chair | 5 min |
| 2 | Portfolio dashboard — agents by control level, KPI breaches, incidents | IT operations | 10 min |
| 3 | Go-live decisions (C4, contested C3) | Business owner presents | 20 min |
| 4 | Material-change decisions | AI team presents | 15 min |
| 5 | Incidents and escalations since last meeting | Risk & Compliance | 10 min |
| 6 | Framework changes / exceptions | Chair | 10 min |
| 7 | AOB and next actions | Chair | 5 min |

## Decision record template

Copy one block per decision into the minutes.

```
Decision ID:        GOV-YYYY-NNN
Date:               YYYY-MM-DD
Agent / use case:   <name> (registry ID: <id>)
Control level:      C_ (base C_, override: <yes/no>)
Decision type:      Go-live | Material change | Incident response | Exception | Decommission
Question:           <the single decision being made>
Decision:           Approved | Approved with conditions | Rejected | Deferred
Conditions:         <controls or evidence required before/after>
Rationale:          <why — risk, controls, residual risk accepted>
Dissent:            <any recorded objection>
Owner / due date:   <who> / <when>
```

## Go-live submission template

What a team brings to the board for a C4 (or contested C3) go-live:

- The completed [risk assessment](../02-risk-assessment/agent-risk-model.md) and assigned level.
- The completed [go-live readiness gate](../03-checklists/go-live-readiness.md).
- The relevant [EU AI Act](../03-checklists/eu-ai-act-agent-checklist.en.md) and
  [DORA](../03-checklists/dora-ict-risk-checklist.en.md) checklists.
- The draft [registry entry](../../templates/agent-registry-entry.md).
- One slide of residual risk the owner is asking the board to accept.
