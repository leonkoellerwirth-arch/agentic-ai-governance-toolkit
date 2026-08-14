# Provider and model dependency

The agent you govern is partly somebody else's system. The model can change without your release,
the provider can retire it, and the terms under which your data is processed are not yours to set.
This is the **sector-independent** minimum for keeping that dependency visible. The DORA checklist
carries the contractual and third-party duties for defined financial entities; everyone else still
has the dependency, just without a regulator naming it.

> This is a practitioner's toolkit, not legal advice. Contractual and data-protection requirements
> depend on your jurisdiction, sector, and arrangement — see the [checklists](../03-checklists/).

## What to record per agent

These belong in the [agent registry entry](../../templates/agent-registry-entry.md), next to the
owner and the control level — not in a separate spreadsheet that ages quietly.

| Field | Why it matters |
|---|---|
| Provider and model | The `model` / `provider` fields also appear per event in the [audit trail](../05-monitoring/logging-requirements.md), so claims about which model decided are checkable. |
| Version, and whether it is pinned | An unpinned model is a dependency that changes without a release of yours. |
| Hosting and region | Where inference happens, and where the data goes to get there. |
| Data sent | Which categories leave your boundary, per the agent's action space. |
| Training on your inputs | Whether the provider may train on what you send. Record the answer, not the assumption. |
| Fallback | What this agent runs on if the provider is unavailable — including "nothing, it stops". |

"Nothing, it stops" is a legitimate answer. An unrecorded assumption that something else would take
over is not.

## Concentration

Count it at the organization level, not per agent:

- How many production agents depend on one provider?
- What is the highest control level among them? A single provider carrying your only C4 agent is a
  different exposure from the same provider carrying five C1 agents.
- Which business functions stop if that provider is unavailable for a day?

The number that matters is not how many providers you use. It is **what breaks when the one you use
most is down**.

## Change you do not control

Three failure modes, in rising order of how often they are missed:

1. **Announced deprecation.** Manageable — it has a date.
2. **Silent model update.** The endpoint stays, the behaviour moves. Your evaluation results age
   without anything visibly changing. This is what pinning and periodic re-evaluation are for.
3. **Terms or region change.** Nothing about the agent changes; what changes is what you are
   allowed to send it.

Each is a **material change** trigger — see [decision rights](decision-rights.md). Model or provider
change is exactly the case where a re-assessment is cheap and skipping it is invisible.

## Exit

For every production agent, one recorded sentence answering: *could this run on a different model,
and what would it cost?*

- **C1–C2:** an answer in the registry is enough.
- **C3:** the answer is tested at least once — the agent has run against an alternative model, and
  the quality difference is recorded.
- **C4:** the alternative is available, and switching to it is part of the
  [incident runbook](../05-monitoring/incident-response.md).

Exit planning fails when it is written as a project rather than a property of the agent. Kept in
the registry, it is one field per agent that someone can be asked about.

## Where this connects

- [Agent registry entry](../../templates/agent-registry-entry.md) — where the fields live.
- [Logging requirements](../05-monitoring/logging-requirements.md) — `model` / `provider` per event.
- [Incident response](../05-monitoring/incident-response.md) — provider outage as a rehearsed scenario.
- The DORA checklist ([EN](../03-checklists/dora-ict-risk-checklist.en.md) ·
  [DE](../03-checklists/dora-ict-risk-checklist.de.md)), section 4 — third-party risk and
  contractual provisions, for entities DORA binds.
