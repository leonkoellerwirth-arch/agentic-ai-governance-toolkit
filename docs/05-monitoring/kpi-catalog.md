# KPI catalog

A starting set of indicators for agents in operation, grouped into **operational**, **risk**, and
**quality**. Pick the handful that matter for a given agent and wire thresholds into monitoring; not
every agent needs every KPI, but every C2+ agent needs some from each group.

> This is a practitioner's toolkit, not legal advice. Thresholds below are illustrative — set your
> own from your risk appetite and a baselining period.

## Operational KPIs — is the agent healthy?

| KPI | What it measures | Example threshold |
|-----|------------------|-------------------|
| Availability | Successful runs / attempted runs | < 99% over a day → alert |
| Latency (p95) | Time to complete a task | > agreed SLA → alert |
| Throughput | Tasks handled per period | Sudden drop vs. baseline → investigate |
| Provider errors | Failed external model/API calls | Spike vs. baseline → check dependency |
| Cost per task | Token/compute cost | > budget → review |

## Risk KPIs — is the agent staying inside its guardrails?

| KPI | What it measures | Example trigger |
|-----|------------------|-----------------|
| Blocked-action rate | Actions refused by the action-space whitelist | Rising trend → probe intent / prompt drift |
| Escalation rate | Share of tasks handed to a human | Above or below the expected band → investigate |
| Override / reversal rate | Human corrections of agent actions | > threshold → the agent is not trustworthy yet |
| Out-of-tolerance events | Actions above value/scope limits | Any → review; repeated → restrict |
| PII / sensitive-data events | Detected handling of sensitive data outside scope | Any → incident path |
| Time since last re-assessment | Governance freshness | Past due date → block changes / escalate |

## Quality KPIs — is the agent doing a good job?

| KPI | What it measures | Example trigger |
|-----|------------------|-----------------|
| Task success rate | Tasks completed correctly (sampled/validated) | Falling trend → retrain / narrow scope |
| Human-approval acceptance | Share of agent proposals a human accepts | Low → the agent is adding little value |
| Complaint / rework rate | Downstream corrections attributable to the agent | Rising → quality regression |
| Confidence calibration | Agreement between stated confidence and correctness | Miscalibration → tighten the escalation trigger |

## Using these

- Feed the same events into the [logging requirements](logging-requirements.md) so the KPIs are
  computable from the audit trail.
- The [`log_analyzer`](../../evaluator/README.md) in the evaluator is a worked example of checking an
  agent's logs against thresholds like these.
- A breach follows the [escalation paths](../01-agent-lifecycle/lifecycle-overview.md#escalation-paths).
