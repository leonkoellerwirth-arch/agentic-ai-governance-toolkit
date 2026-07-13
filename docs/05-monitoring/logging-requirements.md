# Logging requirements — the audit-trail minimum

If it is not logged, it did not happen — you cannot govern, monitor, or investigate an agent you
cannot reconstruct. This is the **minimum** an agent must log. Higher control levels (C3–C4) demand a
tamper-evident trail (append-only, integrity-protected).

> This is a practitioner's toolkit, not legal advice. Align retention and personal-data handling with
> your own data-protection and records policies.

## The principle

**Every decision and every action leaves exactly one record**, before or as it happens — never
reconstructed after the fact. Planning, tool/action execution, review/verdict, human-gate decisions,
and errors are all events on the same trail.

## Minimum fields per event

| Field | Why |
|-------|-----|
| `timestamp` | When it happened (UTC, ordered). |
| `agent_id` / `version` | Which agent, and which version of it. |
| `run_id` / `step_id` | Correlate the steps of one task. |
| `event_type` | `plan` · `action` · `review` · `gate_decision` · `escalation` · `error`. |
| `actor` | The agent role, or the human on a gate decision. |
| `action` + `parameters` | What was attempted (parameters redacted/minimized as needed). |
| `action_in_scope` | Whether it was inside the action-space whitelist. |
| `outcome` | `success` · `blocked` · `escalated` · `error`. |
| `model` / `provider` | Which model decided — especially if an external provider was used. |
| `confidence` | Where the agent produces one, to support calibration KPIs. |
| `data_categories` | Classes of data touched (e.g. `personal`), not the data itself. |
| `human_decision` | On a gate: `approve` · `reject` · `edit`, and who. |
| `correlation_id` | Link to the business transaction/case. |

## What must never be logged

- Secrets, credentials, or full payment/credential data.
- Raw special-category personal data. Log **that** it occurred and its category, not the content.
- Anything that would turn the audit trail into a new data-protection liability.

## Example event (JSONL)

One line per event; the audit trail is a stream of these. This is the shape the evaluator's
[`log_analyzer`](../../evaluator/README.md) reads.

```json
{"timestamp": "2026-01-15T09:31:07Z", "agent_id": "servicing-agent", "version": "2.3.0", "run_id": "r-8842", "step_id": "s-3", "event_type": "gate_decision", "actor": "human:clerk-014", "action": "update_address", "action_in_scope": true, "outcome": "success", "model": "local-llm", "data_categories": ["personal"], "human_decision": "approve", "correlation_id": "case-55231"}
```

## Retention and access

- Retain long enough to satisfy audit, incident investigation, and applicable record-keeping duties;
  define the period per agent and per data category.
- Restrict read access; the trail itself is sensitive.
- For C3–C4, make the trail **append-only and integrity-protected** so a compromised agent cannot
  rewrite its own history.
