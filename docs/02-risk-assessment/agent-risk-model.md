# Agent risk model

Six dimensions describe how much control an AI agent needs. Each is scored **1–5** against the
anchor that best matches the agent as it is actually deployed — not as it might ideally behave. The
scores aggregate into a control-intensity level (C1–C4); see
[`scoring-rubric.md`](scoring-rubric.md) for the aggregation and the minimum controls per level.

> This is a practitioner's toolkit, not legal advice. The model helps you structure a risk
> conversation; it does not certify compliance with any law or standard.

## How to use it

1. For each of the six dimensions, pick the score (1–5) whose anchor best describes the agent.
2. When in doubt between two anchors, choose the higher one and record why.
3. Score the agent **as deployed**: its real autonomy, its real action space, the real data it
   touches. A capability that is switched off today is a change to re-assess, not a lower score.
4. Feed the scores to the evaluator (`agent-eval score --input …`) or aggregate them by hand using
   the [scoring rubric](scoring-rubric.md).

The dimensions are deliberately independent: two of them (action space, reversibility) describe what
the agent can do to the world, two (data sensitivity, blast radius) describe how far harm reaches,
and two (autonomy, explainability) describe how much a human can see and intervene.

## The six dimensions

<!-- GENERATED:dimensions START (source: evaluator/src/agent_evaluator/rubric.yaml — regenerate with: agent-eval render-docs) -->
### Autonomy

_How much can the agent act without a human in the loop?_

| Score | Anchor |
|:-----:|--------|
| 1 | Purely assistive — proposes drafts a human must review and submit. |
| 2 | Suggests actions and pre-fills them; a human approves each one. |
| 3 | Acts on its own within a narrow, pre-approved scope; humans spot-check. |
| 4 | Acts autonomously across a broad scope; humans review exceptions only. |
| 5 | Fully autonomous — decides and acts with no routine human confirmation. |

### Action space

_What can the agent actually do to systems and the outside world?_

| Score | Anchor |
|:-----:|--------|
| 1 | Read-only — retrieves and summarizes; changes nothing. |
| 2 | Writes to low-stakes or sandbox stores (drafts, tickets, notes). |
| 3 | Writes to systems of record the business relies on. |
| 4 | Writes to core or regulated systems (ledgers, customer master data). |
| 5 | Acts on the outside world — payments, external messages, irreversible orders. |

### Reversibility

_How easily can an action be undone?_

| Score | Anchor |
|:-----:|--------|
| 1 | Every action is trivially reversible; no external effect. |
| 2 | Reversible with routine effort inside the same system. |
| 3 | Reversible only through a manual, tracked correction process. |
| 4 | Largely irreversible; remediation is costly or partial. |
| 5 | Irreversible external effect — funds moved, message sent, contract formed. |

### Data sensitivity

_How sensitive is the data the agent can read or write?_

| Score | Anchor |
|:-----:|--------|
| 1 | Public or non-sensitive data only. |
| 2 | Internal, non-personal business data. |
| 3 | Personal data (GDPR-relevant). |
| 4 | Large-scale or financial personal data, or confidential business data. |
| 5 | Special-category personal data or secrets (health, biometrics, credentials). |

### Explainability & traceability

_Can each decision be reconstructed and explained afterwards?_

| Score | Anchor |
|:-----:|--------|
| 1 | Deterministic and fully logged; every decision reconstructable. |
| 2 | Mostly deterministic; decisions logged with their rationale. |
| 3 | Model-driven, but each step is logged and attributable. |
| 4 | Model-driven with limited insight into why a decision was made. |
| 5 | Opaque — outputs cannot be reliably explained or reproduced. |

### Blast radius

_How far does a bad action reach?_

| Score | Anchor |
|:-----:|--------|
| 1 | Affects a single user or a single internal task. |
| 2 | Affects one team or one process. |
| 3 | Affects a business unit or a defined customer segment. |
| 4 | Affects many customers or a critical business function. |
| 5 | Enterprise-wide or broad customer impact; potential systemic effect. |
<!-- GENERATED:dimensions END -->

## From scores to controls

The six scores sum to a total between 6 and 30, which maps to a control-intensity band. Because some
risks are categorical rather than additive — moving money externally is never "light-touch" — a
single extreme dimension can raise the required band regardless of the total. Both the bands and
those overrides are defined in [`scoring-rubric.md`](scoring-rubric.md), and both the documentation
and the evaluator read them from one source of truth: `evaluator/src/agent_evaluator/rubric.yaml`.
