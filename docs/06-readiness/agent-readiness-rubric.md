# Agent readiness — can the organization carry what it is running?

The [risk model](../02-risk-assessment/agent-risk-model.md) answers one half of the question: how
much control does *this agent* need? This page is the other half. It asks whether the organization
running it actually has that control.

The two are deliberately separate:

| | Question | Source of truth |
|---|---|---|
| **Exposure** | What your agents can do to you | [`rubric.yaml`](../../evaluator/src/agent_evaluator/rubric.yaml) |
| **Readiness** | Whether you can carry it | [`readiness.yaml`](../../evaluator/src/agent_evaluator/readiness.yaml) |

> **Readiness is not absolute.** It is measured against the control level the organization actually
> operates. An organization running only C1 agents with C1 controls is ready. One running C4 agents
> with C2 controls is not — however much governance it has on paper, and even if it has more of it
> than the first.

Every dimension below is **derived** from a demand the toolkit already makes: the C1–C4 control
lists, the [go-live gate](../03-checklists/go-live-readiness.md), the
[logging requirements](../05-monitoring/logging-requirements.md), the
[KPI catalog](../05-monitoring/kpi-catalog.md),
[decision rights](../04-operating-model/decision-rights.md), and the
[RACI](../04-operating-model/roles-and-raci.md). Each dimension records which, so the claim that
nothing here is invented is checkable rather than asserted. Where a number is a judgement rather than
a derivation, it is recorded in the
[policy-decision register](../02-risk-assessment/policy-decisions.md) with what it accepts as a cost.

**Not a certification, and not legal advice.** This is a reference pattern. The evaluator that
computes a result from these rules proves that the result follows from the rules — it does not prove
that the rules are right.

## Before scoring anything: the precondition

Not a dimension and not scored. A control level cannot be determined correctly before the regulatory
classification is known, so a missing answer taints the whole result rather than costing a point.

<!-- GENERATED:readiness_preconditions START — edit readiness.yaml, then run `agent-eval render-docs` -->
**regulatory_classification** — Has the regulatory classification been determined per agent — your role in the value chain (provider / deployer) and the agent's risk category?

_If unanswered:_ The exposure figure is regulatorily incomplete. Report the readiness result with this warning attached; do not present it as an assessment of regulatory standing.
<!-- GENERATED:readiness_preconditions END -->

## What each control level requires

The required level per dimension, by the control level of the agent being carried. Read a row as:
*an organization running a C3 agent needs at least this much of this dimension.*

<!-- GENERATED:readiness_required START — edit readiness.yaml, then run `agent-eval render-docs` -->
| Dimension | C1 | C2 | C3 | C4 |
|-----------|:--:|:--:|:--:|:--:|
| Inventory clarity | R1 | R2 | R2 | R3 |
| Action space and intervention | R1 | R2 | R2 | R3 |
| Reconstructability | R1 | R2 | R3 | R3 |
| Stop and roll back | R0 | R1 | R2 | R3 |
| Independent assurance | R1 | R1 | R2 | R3 |
| Currency | R1 | R2 | R2 | R3 |
<!-- GENERATED:readiness_required END -->

Two rows are worth reading twice. **Reconstructability** is the only dimension pulled to R3 already
at C3 — because every other gap can be closed going forward, while a decision that was never
traceable cannot be made traceable afterwards. **Independent assurance** deliberately stays at R1 for
C2, because the C2 control list demands only a named, signing owner; demanding more here would make
this rubric ask more than the exposure rubric does. Both are recorded as decisions, with their costs.

## The dimensions

Each is scored R0–R3 against the anchor that best describes the organization **as it actually
operates**. Every anchor is written to be falsifiable: a reviewer must be able to ask for the
evidence and be told no. The *probe* is that question in its shortest form.

<!-- GENERATED:readiness_dimensions START — edit readiness.yaml, then run `agent-eval render-docs` -->
### Inventory clarity

_Does the organization know what it runs?_

| Score | Anchor |
|:-----:|--------|
| R0 | No list exists. Nobody can say how many agents are in production. |
| R1 | A list exists and names an accountable owner for at least half of the agents in production. |
| R2 | Every agent in production is in the registry with a named owner, a documented intake, and an assigned control level (C1–C4) together with the reasoning for it. |
| R3 | As R2, plus the value-chain role (provider / deployer) is determined per agent, model and provider dependencies are inventoried, and a periodic reconciliation of the registry against actually running systems takes place — and finds discrepancies. |

**Required** — C1 → R1 · C2 → R2 · C3 → R2 · C4 → R3

**Probe** — "Name your third-riskiest agent and its control level." At R2 the answer takes minutes, not days.

**Derived from**

- C1 control: owner recorded in the agent registry
- C2 control: documented use-case intake and risk assessment on file
- Go-live gate rows 1 and 11
- Provider and model dependency: fields to record per agent, exit by control level
- EU AI Act checklist 1.2–1.4 and 6.4; DORA checklist 1.1–1.3

### Action space and intervention

_Is what the agent can do bounded — and can a human get in between?_

| Score | Anchor |
|:-----:|--------|
| R0 | The agent can do whatever its credentials allow. No defined action space. |
| R1 | The action space is documented but not technically enforced — a breach would be possible and would not be noticed. |
| R2 | The action space is technically enforced: out-of-scope actions are refused, and the refusal path is covered by a test. Where required, an explicit human gate (approve / reject) exists, not merely a notification. |
| R3 | As R2, plus per-action pre-authorization for C4 agents, and the blocked-action rate is watched as a KPI rather than merely logged. |

**Required** — C1 → R1 · C2 → R2 · C3 → R2 · C4 → R3

**Probe** — "Show me the test case in which the agent refuses an action outside its action space." Without that test case, R2 is not demonstrated.

**Derived from**

- C3 control: human-in-the-loop for in-scope actions (explicit approve/reject)
- C4 control: per-action pre-authorization by an accountable human
- Go-live gate rows 3 and 4
- EU AI Act checklist 3.1–3.3; DORA checklist 1.4 (least privilege)

### Reconstructability

_Can every decision be explained after the fact?_

| Score | Anchor |
|:-----:|--------|
| R0 | Application logs exist, but no decision trail. Why the agent acted cannot be established. |
| R1 | Actions are logged; the mandatory fields are incomplete. A single run can be reconstructed with effort. |
| R2 | Every decision and action produces exactly one record carrying the mandatory fields (run and step id, event type, actor, action and in-scope flag, outcome, model, data categories, human decision, correlation id). No secrets and no raw special-category data. Any given case is traceable to prompt, context, and tool calls within 24 hours. |
| R3 | As R2, plus append-only and integrity-protected, retention defined per agent and data category, and read access restricted — a compromised agent cannot rewrite its own history. |

**Required** — C1 → R1 · C2 → R2 · C3 → R3 · C4 → R3

**Probe** — "Take a case from last month and reconstruct why the agent chose what it chose." Run it; do not accept a description of the log schema.

**Derived from**

- C1 control: standard logging, errors surfaced to the owning team
- C4 control: continuous monitoring with a tamper-evident audit trail
- Go-live gate row 9; the logging requirements in full
- EU AI Act checklist 4.1; DORA checklist 2.2

> **Self-assessment caveat.** The dimension a self-assessment most reliably overstates. R2 is proven by performing the reconstruction, not by asserting that the fields exist.

### Stop and roll back

_Can the organization halt the agent and undo what it did?_

| Score | Anchor |
|:-----:|--------|
| R0 | No defined stop. One would have to revoke credentials or shut the service down. |
| R1 | A stop path is described but has never been exercised. |
| R2 | Kill-switch and rollback are documented and have been triggered at least once under realistic conditions, with a record and a measured time to effect. |
| R3 | As R2, plus a rehearsed incident runbook; failure scenarios played through (model or API outage, degraded output, timeout, confidently wrong output); and reporting paths for serious incidents named, time-bound, and exercised. |

**Required** — C1 → R0 · C2 → R1 · C3 → R2 · C4 → R3

**Probe** — "When was the kill-switch last triggered, and how long did it take to take effect?" A documented but never-triggered kill-switch is R1, not R2.

**Derived from**

- C3 control: documented rollback and kill-switch procedure
- C4 control: tested kill-switch and incident runbook
- Go-live gate rows 5 and 8
- Incident response: the runbook, stop/rollback by control level, rehearsed scenarios
- EU AI Act checklist 3.4 and 6.1–6.2; DORA checklist 3.1–3.3 and 5.1–5.3

### Independent assurance

_Does anyone who did not build it check it?_

| Score | Anchor |
|:-----:|--------|
| R0 | Whoever builds also signs off. |
| R1 | Sign-off by a named owner, but without functional separation from delivery. |
| R2 | The risk assessment sits with a second line that did not build it; its sign-off is a precondition for go-live from C3 upward; decision rights are written down by control level. |
| R3 | As R2, plus a governance board for C4 agents and for every exception to a mandatory control, and periodic third-line assurance over the programme rather than over individual cases. |

**Required** — C1 → R1 · C2 → R1 · C3 → R2 · C4 → R3

**Probe** — "Show me the document in which the second line recorded its finding — not the approval, the finding." The dimension where self-image and reality diverge furthest.

**Derived from**

- C3 control: independent (2nd-line) review before go-live
- C4 control: 2nd- and, where relevant, 3rd-line review; board visibility
- Go-live gate row 15; decision rights; RACI (builders do not sign off their own risk)

### Currency

_Is the finding from today, or from go-live?_

| Score | Anchor |
|:-----:|--------|
| R0 | The assessment is from go-live. Nobody has looked since. |
| R1 | KPIs exist, but without thresholds or without alerting; re-assessment is ad hoc and undocumented. |
| R2 | KPIs from all three groups (operational, risk, quality) are wired with thresholds and alerting; "time since last re-assessment" is itself a monitored KPI; material change is defined and demonstrably triggers a re-assessment. |
| R3 | As R2, plus no agent in production is past its cadence (C2 annually, C3 and C4 quarterly), and threshold breaches follow an escalation path with evidence that it has been used. |

**Required** — C1 → R1 · C2 → R2 · C3 → R2 · C4 → R3

**Probe** — "Which agent is currently furthest past its re-assessment date?" At R3 the answer is 'none', and the questioner can see how that is known.

**Derived from**

- C1 control: re-assess on any material change
- C2 control: operational KPIs monitored; re-assessment at least annually
- C3/C4 control: re-assessment quarterly
- Go-live gate rows 10 and 14; KPI catalog; decision rights (material change)
<!-- GENERATED:readiness_dimensions END -->

## How the result is put together

<!-- GENERATED:readiness_aggregation START — edit readiness.yaml, then run `agent-eval render-docs` -->
- **Exposure** — `highest_level_in_production`. Exposure follows the single riskiest agent, not the representative one. A risk function reads that as correct; a delivery function reads it as unfair. State the choice; do not bury it.
- **Required, per dimension** — `max_over_agents`.
- **Achieved, per dimension** — `min_over_triggering_agents`. Required is the highest minimum any agent in production triggers. Achieved is the LOWEST level reached by an agent that triggers that requirement.
- **Coverage** — `dimensions_meeting_required_out_of_total`. No 0–100 index value is produced. A single number invites optimizing the number instead of the control; a required/achieved pair per dimension does not. "4 of 6 at exposure C3" is shareable and cannot be quoted without its exposure.
- **Detail** — Always report how many agents sit below target, not only that the dimension does — "1 of 3 C4 agents below target" separates a single site from a systemic gap, which the bare achieved/required pair cannot.
- **Not applicable** — An organization with no agents in production has no gap by construction. Report "exposure: none in production — the rubric does not apply". Never report full coverage, or the rubric measures restraint as maturity.
- **How this is gamed** — Name the way this is gamed, because it is the obvious one: decommissioning the single riskiest agent lowers the reported exposure, and every dimension measured against it, without one control having improved. Where exactly one agent sets the exposure, the result says so — a figure that hangs on one system should be read as hanging on one system.
<!-- GENERATED:readiness_aggregation END -->

The minimum rule is a **deliberately non-compensatory decision rule**, not a proven correctness: a
weak critical control should not be compensated by strong values elsewhere. It is brittle by design,
and the cost is recorded in
[`PD-R-AGG-001`](../02-risk-assessment/policy-decisions.md) — one agent at R1 drags a dimension to R1
however good the other twenty are, and the organization will experience that as unfair.

## Known simplifications

Stated, not hidden. An honest gap is cheaper than a silent one.

<!-- GENERATED:readiness_simplifications START — edit readiness.yaml, then run `agent-eval render-docs` -->
**Identity and access management is not a separate dimension.**

Who may grant an agent access to which system is only partially covered — by `oversight` (what the agent may do) and `traceability` (which data categories it touches). An agent can be technically confined to its documented action space and still hold credentials reaching systems that never appear in it. That is an IAM problem, not an action-space problem. Treat this as a known simplification, not as coverage.

**Provider dependency is a recorded fact, not a dimension of its own.**

What to record per agent, concentration at the organization level, and exit expectations by control level are now sector-independent (see the provider dependency doc), so `inventory` at R3 has something real to point at. What stays out of reach: contractual provisions and regulated concentration risk, which live in the DORA checklist and bind defined financial entities only. The rubric measures whether you know your dependency — not whether your contracts cover it.
<!-- GENERATED:readiness_simplifications END -->

## Running it

```bash
agent-eval readiness --input evaluator/examples/org-readiness-demo.yaml
agent-eval readiness --input evaluator/examples/org-readiness-demo.yaml --json
```

The input lists every agent in production with the control level from `agent-eval score` and the
organization's honest R0–R3 self-assessment for that agent. The command exits non-zero when any
dimension sits below its required level, so it can be used as a gate.

---

*Part of the [agentic-ai-governance-toolkit](../../README.md). Reference pattern, not a framework.
Not legal advice.*
