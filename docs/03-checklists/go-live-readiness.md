# Go-live readiness gate

The gate an agent must pass before it goes to production (lifecycle phase 5). It pulls the essential
checks into one sign-off. Scale the depth to the control level: **C1** needs the basics; **C3–C4**
need every row, with independent (2nd-line) sign-off.

> This is a practitioner's toolkit, not legal advice. Adapt the gate to your own release process and
> obligations. Do not go live with an open item unless the accountable owner has explicitly accepted
> the residual risk in writing.

Fill **Status** with ✓ / ✗ / n/a. The gate is passed when every applicable row is ✓ or an accepted,
documented exception.

## Risk and controls

| # | Gate criterion | Min. level | Evidence | Status |
|:-:|----------------|:----------:|----------|:------:|
| 1 | Risk assessment complete; **control level (C1–C4) assigned** and signed off. | C1 | Assessment record | ☐ |
| 2 | The **minimum controls** for the level are implemented (see [scoring rubric](../02-risk-assessment/scoring-rubric.md)). | C1 | Control mapping | ☐ |
| 3 | **Action space** is whitelisted; the agent refuses out-of-scope actions. | C1 | Design + test | ☐ |
| 4 | **Human-in-the-loop** is in place for in-scope actions. | C3 | Control design | ☐ |
| 5 | **Kill-switch / stop** procedure exists and has been tested. | C3 | Test record | ☐ |

## Validation

| # | Gate criterion | Min. level | Evidence | Status |
|:-:|----------------|:----------:|----------|:------:|
| 6 | Acceptance tests passed for the agent's intended behaviour. | C1 | Test results | ☐ |
| 7 | **Light red-teaming** done: attempts to break the action space, leak data, or bypass the human gate. | C2 | Red-team notes | ☐ |
| 8 | **Failure scenarios** rehearsed (model/API outage, degraded output, timeout). | C2 | Playbook | ☐ |

## Observability

| # | Gate criterion | Min. level | Evidence | Status |
|:-:|----------------|:----------:|----------|:------:|
| 9 | **Audit-trail logging** meets the [logging requirements](../05-monitoring/logging-requirements.md). | C1 | Log sample | ☐ |
| 10 | **KPIs and thresholds** with alerting are configured (see [KPI catalog](../05-monitoring/kpi-catalog.md)). | C2 | Monitoring config | ☐ |

## Accountability and compliance

| # | Gate criterion | Min. level | Evidence | Status |
|:-:|----------------|:----------:|----------|:------:|
| 11 | **Accountable owner** named; **registry entry** complete (see [agent registry](../../templates/agent-registry-entry.md)). | C1 | Registry entry | ☐ |
| 12 | Relevant **checklists** worked through ([EU AI Act](eu-ai-act-agent-checklist.en.md), [DORA](dora-ict-risk-checklist.en.md)). | C2 | Completed checklists | ☐ |
| 13 | **Transparency / communication** duties met (users informed, content labelled where required). | C2 | Disclosure evidence | ☐ |
| 14 | **Re-assessment cadence** scheduled; change classes defined. | C1 | Re-assessment plan | ☐ |
| 15 | **Independent (2nd-line) sign-off** obtained. | C3 | Sign-off record | ☐ |

---

**Go-live decision:** ☐ Approved ☐ Approved with documented exceptions ☐ Rejected

Owner: ____________________  ·  Risk (2nd line): ____________________  ·  Date: __________
