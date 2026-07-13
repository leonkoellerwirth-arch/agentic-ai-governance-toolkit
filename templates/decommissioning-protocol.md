# Decommissioning protocol

The orderly retirement of an agent (lifecycle phase 7). Retiring an agent badly leaves live
credentials, orphaned integrations, and a broken audit trail. Work the checklist; get the sign-off.

> This is a practitioner's toolkit, not legal advice. Align retention and data handling with your own
> data-protection and records policies.

## 1. Trigger and decision

- **Agent (registry ID):**
- **Reason:** ☐ Superseded ☐ No longer needed ☐ Risk/incident ☐ Provider/model retired ☐ Other:
- **Decommissioning approved by:** (per [decision rights](../docs/04-operating-model/decision-rights.md) — C4 needs the board)
- **Target date:**

## 2. Wind-down checklist

| # | Step | Done | Evidence |
|:-:|------|:----:|----------|
| 1 | Stakeholders and affected users **informed**; cut-over or manual fallback agreed. | ☐ | |
| 2 | Agent **stopped** from taking new tasks; in-flight tasks drained or handed to a human. | ☐ | |
| 3 | **Access revoked** — API keys, service accounts, tokens, system permissions disabled. | ☐ | |
| 4 | **Integrations** disconnected; downstream systems confirmed unaffected. | ☐ | |
| 5 | **External provider** arrangements terminated / off-boarded; register updated. | ☐ | |
| 6 | **Data** handled per policy — export, delete, or retain as required; personal data addressed. | ☐ | |
| 7 | **Audit trail retained** for the required period, read-only, still accessible for investigation. | ☐ | |
| 8 | **Registry** updated: status → Decommissioned, with date and reason. | ☐ | |
| 9 | **Post-retirement check** after N days: no orphaned jobs, calls, or costs. | ☐ | |

## 3. Sign-off

- **Decommissioning completed by / date:**
- **Risk (2nd line) confirmation:**
- **Residual items / follow-ups:**
