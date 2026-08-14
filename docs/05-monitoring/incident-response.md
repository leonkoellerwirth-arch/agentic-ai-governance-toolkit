# Incident response — stopping an agent and cleaning up after it

Detection without response is theatre. [Monitoring](kpi-catalog.md) tells you something is wrong;
this tells you what happens next. It is the **sector-independent** minimum: the DORA checklist
covers incident duties for defined financial entities, but an agent that acts on your systems needs
a stop path whether or not a regulator asks for one.

> This is a practitioner's toolkit, not legal advice. External reporting duties depend on your
> sector, your role, and the system — see the [checklists](../03-checklists/) and confirm with your
> compliance function.

## What counts as an agent incident

Not every error. An incident is any event where the agent **acted outside what it was allowed to
do, or inside it with an effect you did not intend**:

- An action outside the documented action space succeeded rather than being blocked.
- The agent acted on data categories it should not touch.
- A wrong-but-confident output was accepted downstream before anyone noticed.
- A human gate was bypassed, auto-approved, or approved without the information it needed.
- The audit trail is incomplete for a run — you cannot reconstruct what happened.
- The agent's provider or model changed underneath it without a re-assessment.

The last two are the ones organizations classify as "not an incident" and later wish they had not.

## Severity follows the control level

An incident's severity is not a property of the event alone — it is the event seen through the
[control level](../02-risk-assessment/scoring-rubric.md) of the agent that caused it.

| Severity | Typical trigger | Response |
|---|---|---|
| **Low** | Blocked out-of-scope action, contained error, no external effect | Log, count as a KPI, review in the normal cadence |
| **Medium** | Repeated blocked actions, degraded output quality, gate latency breaching threshold | Owner informed same day; re-assessment considered |
| **High** | An out-of-scope action succeeded · special-category data touched · gate bypassed | Stop the agent; owner and 2nd line informed; rollback assessed |
| **Critical** | Effect outside the organization · irreversible action · C3/C4 agent behaving outside its envelope | Kill switch; incident lead named; governance body informed |

Any incident on a **C4** agent starts at High. The control level is a statement about what the
agent can do to you — it does not stop being true during an incident.

## The runbook

Five steps, in order. The order is the point: containment before diagnosis, always.

1. **Contain.** Stop the agent — kill switch, credential revocation, or feature flag. Record the
   time you triggered it and the time it took effect. Those are two different numbers.
2. **Assess reach.** Which runs, which cases, which records? The `run_id` / `correlation_id` fields
   in the [audit trail](logging-requirements.md) are what make this minutes rather than days.
3. **Correct.** Roll back what can be rolled back; list what cannot. An action you cannot undo is a
   finding about the agent's design, not only about this incident.
4. **Communicate.** Owner, 2nd line, and affected business function. Escalate per
   [decision rights](../04-operating-model/decision-rights.md). Decide explicitly whether an
   external reporting duty applies — and record that decision either way.
5. **Learn.** Write it up, and route it: a control that failed, a threshold that did not fire, or
   an action space that was too wide. Every incident either changes something or is repeated.

## Stop and roll back — expectations by control level

| Level | Expected |
|:-----:|---|
| **C1** | The service can be stopped. No dedicated procedure required. |
| **C2** | A documented stop path with a named owner who can trigger it. |
| **C3** | Kill switch **and** rollback documented, and exercised at least once under realistic conditions, with a record and a measured time to effect. |
| **C4** | As C3, plus a rehearsed incident runbook, named incident lead, and reporting paths that have been walked through — not only written down. |

**A stop path that has never been exercised is not a control.** It is a claim about a control. The
distinction survives contact with an actual incident; the claim does not.

## Scenarios worth rehearsing

Rehearse the ones where the agent keeps running while being wrong — those are harder than a clean
outage and far more common:

- Model or API unavailable, or rate-limited mid-run.
- Timeout leaving a multi-step task half-applied.
- Degraded output quality after a provider-side model update.
- Confidently wrong output that passes the gate because it reads well.
- The kill switch itself failing, or taking longer to take effect than assumed.

## After the incident

- Record it against the agent in the registry. An incident is a **material change** trigger — see
  [decision rights](../04-operating-model/decision-rights.md).
- Feed the numbers back into the [KPI catalog](kpi-catalog.md): time to contain, time to effect,
  and whether the threshold that should have fired did.
- Re-run the [go-live gate](../03-checklists/go-live-readiness.md) rows the incident touched before
  the agent goes back into production. Restarting is a release, not a resumption.
