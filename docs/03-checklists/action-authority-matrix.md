# Action authority matrix

An **example policy**, not a finding. What an agent may do unattended, what a competent person
approves first, and the few things that are refused by design.

The scoring rubric answers how much control an agent needs. This answers the question a reviewer
asks immediately afterwards: *so what is it allowed to do?* Every value below is a judgement call.
The judgements are registered in [policy decisions](../02-risk-assessment/policy-decisions.md)
(`PD-AUTHORITY-*`) with what each one accepts as a cost, and a deployment that adopts them
unchanged has not done the work.

Not legal advice — see [`DISCLAIMER.md`](../../DISCLAIMER.md).

## What this is, and what it is not

[What this maps, and what it does not](../00-scope/regulatory-scope.md) says this project does not
determine whether an obligation applies to a given system, and does not score attainment. A table
that says **forbidden** is a normative judgement, so the two have to be reconciled rather than
left side by side.

The reconciliation: **this is a starting policy, not a derived one.** No row here is deduced from
a legal text, and none is offered as the answer for your deployment. It is one defensible set of
defaults, published so that disagreeing with it is cheap — the disagreement being the actual
exercise. "This enforces nothing" is true and does not settle it; what settles it is that the
values are declared as judgement, registered as judgement, and expected to be replaced.

The enforcing half is a pre-action check in the runtime. A reference implementation is
[`local-agent-pipeline`](https://github.com/leonkoellerwirth-arch/local-agent-pipeline), where the
action space is intersected before the worker ever sees a step.

## How to read it

| Column | Meaning |
|---|---|
| ✓ | Automatic. The agent may do this unattended. |
| ✓ * | Automatic, **conditionally** — the preconditions under "Why each row is where it is" must hold, and named contexts escalate it. |
| H | A competent person approves this instance before it takes effect. |
| H * | Approval, with a narrow carve-out or a stricter case — again, conditions below. |
| ✗ | Refused by design. The attempt is recorded and is itself a finding. |

**Authority depends on the action's own context, never on the control band.** An earlier version
of this file escalated at a band — "automatic below C3" — and that was wrong in both directions: a
band is the sum of six dimensions, so a system full of personal data can score C1, and C3 can
arise with no personal data in it at all. The conditions are now about purpose, data class, scope,
recipient, and whether a prior approval exists. The correction is recorded in
`PD-AUTHORITY-CONDITIONS` rather than quietly applied.

**What makes something forbidden** rather than merely approved is one criterion — *approval cannot
repair it* — in three named limbs, and every refused row has to name the limb it meets:

| Limb | Statement | Rows |
|---|---|---|
| `evidence_destruction` | The action destroys or disables the evidence of itself. | disable oversight |
| `boundary_move` | The action moves the boundary from inside the boundary. | modify own scope |
| `instant_harm` | The harm completes at the instant of the action, so no later control undoes it. | read secrets |

Validation rejects a refusal whose limb is not declared. That is not decoration: an earlier
version of this file refused four things, and two of them met none of its own criterion —
deciding to delete destroys nothing, execution does. Requiring the limb per row is what surfaced
it. Everything else, however severe, is approval with requirements attached, because a refusal
teams route around is worse than a demanding approval they follow.

**Every row names an evidence artifact, including the refused ones.** A refusal that leaves no
trace cannot be audited, and an attempt at a refused action is a finding in its own right.

<!-- GENERATED:authority-matrix START — edit action_authority.yaml, then run `agent-eval render-docs` -->
### Reading

Actions that observe. They leak; they do not change.

| Action | Automatic | Human approval | Forbidden | Evidence |
|---|:---:|:---:|:---:|---|
| Search the internal knowledge base | ✓ * | – | – | Query log with identity, query, retrieved document ids, timestamp |
| Retrieve records containing personal data | ✓ * | – | – | Query log plus the data categories touched, retained per the deletion concept |
| Read credentials, keys or secrets | – | – | ✗ | Policy event naming the attempted secret and the calling step |

### Producing

Actions that create something. Harmless only while nothing consumes it automatically.

| Action | Automatic | Human approval | Forbidden | Evidence |
|---|:---:|:---:|:---:|---|
| Draft a document, message or summary | ✓ * | – | – | Draft stored with model, prompt hash and output hash |
| Classify or tag a record without changing it | ✓ * | – | – | Decision log with input reference, label, confidence |
| Make or trigger a decision on an individual case | – | H | – | Decision record with inputs, rule version, outcome, approver and timestamp |

### Writing inside the boundary

Actions that change state the organisation controls.

| Action | Automatic | Human approval | Forbidden | Evidence |
|---|:---:|:---:|:---:|---|
| Write to its own scratch or working store | ✓ * | – | – | Change log for the working store |
| Modify customer, contract or master data | – | H | – | Change record with before/after values, approver identity and timestamp |
| Execute a pre-approved deletion rule | ✓ * | – | – | Deletion record per run — rule version, scope, counts, legal-hold result |
| Select records for deletion outside an approved rule | – | H * | – | Selection record with criteria, resulting record ids, requester and approver |
| Revoke access on a leaver, expiry or compromise event | ✓ * | – | – | Entitlement change log with the triggering event and its source system |
| Grant access or raise a privilege | – | H | – | Entitlement change record with requester, approver, scope and expiry |
| Change business rules, thresholds, prompts, models or connector configuration in production | – | H | – | Change record with diff, approver, and the release it went out in |
| Execute code, shell commands or infrastructure operations | – | H * | – | Execution log with the exact command, environment and result |
| Export, download or stage a bulk extract | – | H | – | Export record with data categories, row counts, destination and approver |

### Acting on the outside world

Actions a third party observes or receives.

| Action | Automatic | Human approval | Forbidden | Evidence |
|---|:---:|:---:|:---:|---|
| Send a pre-approved templated notification | ✓ * | – | – | Send log with template version, recipient reference and timestamp |
| Compose and send a message outside the organisation | – | H | – | Approval record linking approver, recipient, content hash and send timestamp |
| Initiate a payment or place a binding order | – | H * | – | Payment record with payee, amount, limit check, four-eyes approval and segregation of duties |
| Publish content to a public channel | – | H | – | Approval record with the exact published artifact and its hash |
| Fetch and process external content, URLs or attachments | – | H * | – | Fetch log with source, content hash and the context it was admitted to |
| Call an external API with organisational data | ✓ * | – | – | Call log with endpoint, data categories transmitted, provider and region |

### Acting on itself

Actions that change the agent's own scope, tools or oversight.

| Action | Automatic | Human approval | Forbidden | Evidence |
|---|:---:|:---:|:---:|---|
| Delegate a step to another agent | ✓ * | – | – | Trail entry naming the delegating step, the delegate and the inherited scope |
| Change its own action space, tools, prompts, connectors or roles | – | – | ✗ | Policy event naming the attempted change |
| Disable logging, the audit trail or the human gate | – | – | ✗ | Policy event recorded outside the agent's identity; the absence of expected trail entries is itself the alarm |
<!-- GENERATED:authority-matrix END -->

## Why each row is where it is

A matrix without reasoning is a preference. These are the arguments, and they are the part worth
disagreeing with.

<!-- GENERATED:authority-rationales START — edit action_authority.yaml, then run `agent-eval render-docs` -->
- **Search the internal knowledge base** — Retrieval within an identity-scoped index is the base case. "Identity-scoped" is a precondition, not a property one may assume: full-text search over an unclassified corpus puts privileged communication and HR material into the model context.
  - *Automatic only while:* Authorisation is evaluated before retrieval, not applied to the result afterwards.
  - *Automatic only while:* Every indexed source is classified and approved for the index.
  - *Needs a person when:* The query reaches data classes outside the agent's declared purpose.
  - *Needs a person when:* Retrieval is broad or bulk rather than answering one question.
- **Retrieve records containing personal data** — Processing begins at the first retrieval, not at a score. Requiring approval for every routine service lookup is unworkable; requiring it for bulk, special-category and exceptional access is where the risk actually sits.
  - *Automatic only while:* The purpose is recorded and the retrieval serves it.
  - *Automatic only while:* Field-level least privilege applies; unnecessary attributes are not returned.
  - *Needs a person when:* Special categories of personal data are in scope.
  - *Needs a person when:* The access is bulk, or the output is an unmasked export.
  - *Needs a person when:* The purpose is an exception to the routine one.
- **Read credentials, keys or secrets** — An agent that can read a secret can exfiltrate it, and no later approval recovers from that. Secrets reach tools through the runtime, never through the model context.
- **Draft a document, message or summary** — A draft is harmless while a person stands between it and effect. Once something downstream consumes it, it is that downstream action and must be authorised as one.
  - *Automatic only while:* The draft lands in an isolated draft store.
  - *Automatic only while:* Nothing consumes it automatically.
  - *Needs a person when:* The draft becomes a ticket, a customer record, or a knowledge-base entry.
  - *Needs a person when:* The draft pre-fills a field that another process treats as given.
- **Classify or tag a record without changing it** — "Changes nothing" is not "harmless". Where a label is the input to a consequential decision, the label is the decision, and the control belongs on the label.
  - *Automatic only while:* The label carries no legal, financial or customer-facing consequence.
  - *Needs a person when:* The label drives a consequential outcome — credit, fraud, AML, HR, prioritisation.
- **Make or trigger a decision on an individual case** — Credit, fraud, AML, entitlement, HR and prioritisation decisions carry the consequence that classification only points at. This is the row that matters; the label row is upstream of it.
- **Write to its own scratch or working store** — Scratch space is where persistence, exfiltration, poisoning and retention risks accumulate quietly. Free inside the sandbox; not a general write permission.
  - *Automatic only while:* The store is isolated, quota-bounded and short-lived.
  - *Automatic only while:* Declared data classes are excluded, and a deletion rule applies to what remains.
  - *Needs a person when:* Anything written there is read by another system or another agent.
- **Modify customer, contract or master data** — Master data is what other systems trust. A wrong value propagates silently and is found weeks later by someone who cannot tell where it came from.
- **Execute a pre-approved deletion rule** — Expired retention, confirmed erasure requests and de-duplication are executed on a schedule, not decided ad hoc. Forbidding execution outright would forbid the compliant path.
  - *Automatic only while:* The rule was approved in advance under four eyes and is versioned.
  - *Automatic only while:* A legal-hold check runs immediately before execution.
  - *Automatic only while:* Execution writes an immutable deletion record naming rule version and scope.
  - *Automatic only while:* Selection criteria are part of the approved rule version; the agent supplies no parameter that widens the target set.
  - *Needs a person when:* The scope of a run exceeds the approved rule's expected volume.
- **Select records for deletion outside an approved rule** — An earlier version forbade this outright and was wrong twice over: deciding destroys nothing — execution does — so it fails the refusal criterion, and forbidding it pushes the real risk out of sight. The enforceable control is that whoever selects does not also execute, and that the agent supplies no parameter that widens an approved rule.
  - *Refused when:* The selection is executed in the same step that produced it.
- **Revoke access on a leaver, expiry or compromise event** — Timely removal of access is a control, not a risk. Requiring a human in this path makes the organisation slower at exactly the moment speed is the control.
  - *Automatic only while:* The revocation follows a rule determined in advance, from a traceable source event.
  - *Automatic only while:* A documented break-glass path exists for wrongful revocation.
- **Grant access or raise a privilege** — Widening reach is the direction that needs a decision. It stays inside joiner-mover-leaver; the agent may request, never decide.
- **Change business rules, thresholds, prompts, models or connector configuration in production** — Self-modification is covered elsewhere. This is the neighbouring case that is easy to miss: an agent changing somebody else's production logic, which is a deployment and reviewed as one.
- **Execute code, shell commands or infrastructure operations** — The highest-leverage action in most real deployments and the one most often left implicit. Inside a sealed sandbox it is a working step; anywhere else it is arbitrary capability.
  - *May run unattended if:* No network egress and no credentials are reachable from the sandbox.
  - *May run unattended if:* Writes are confined to an ephemeral workspace; no host mounts, no persistence.
  - *May run unattended if:* CPU, memory, process and wall-clock limits are enforced and a breach aborts the run.
- **Export, download or stage a bulk extract** — This is the exfiltration path, and reading rows one at a time is not the same action as taking all of them at once. Volume is the risk; the per-record rows do not cover it.
- **Send a pre-approved templated notification** — Requiring a human for every transactional confirmation would make the matrix unusable and push teams around it. The control is the template, not the send.
  - *Automatic only while:* The template was approved in advance and is versioned.
  - *Automatic only while:* The recipient comes from the record, not from the model.
  - *Automatic only while:* No free text is generated into the message.
- **Compose and send a message outside the organisation** — The first action here a third party observes. Recall is not a control; the recipient has already read it.
- **Initiate a payment or place a binding order** — Payment operations already run on separation of preparation, checking, approval and execution; an agent may occupy the preparation and execution slots. What must not happen is the agent choosing the counterparty or the amount. An earlier version also refused any instance "without effective prior approval", which was circular — instance approval is the baseline, so that limb refused the very path it required.
  - *Refused when:* The agent selects or alters payee, amount, or the terms of the obligation.
- **Publish content to a public channel** — Publication is irreversible in the only sense that matters: it has been seen. The evidence must be the artifact itself, not a description of it. For a mandatory disclosure "a named person approved it" is not enough — the responsible function has to.
  - *Needs the responsible function, not any approver, when:* The publication is a regulatory disclosure or a market communication.
- **Fetch and process external content, URLs or attachments** — The standard route for prompt injection, server-side request forgery and data egress. Allowlisted and isolated it is routine; open, it is an untrusted instruction channel.
  - *May run unattended if:* The source is on an approved allowlist and is fetched into an isolated context.
- **Call an external API with organisational data** — The control point is the approved transfer, not the agent's overall score. The evidence must name the region, because the contractual question is where processing happened.
  - *Automatic only while:* The call sits inside a data flow that was approved for this provider, region and purpose.
  - *Needs a person when:* The provider, the data category, the region or the purpose is new.
- **Delegate a step to another agent** — Delegation is where an action space quietly widens, and low control levels do not protect against injection or responsibility diffusion. The technical inheritance is the control.
  - *Automatic only while:* The delegate holds an inherited capability token it cannot widen.
  - *Automatic only while:* The delegate is in the agent register, with resource and depth limits.
  - *Needs a person when:* The delegate has external access or a privilege the caller lacks.
- **Change its own action space, tools, prompts, connectors or roles** — The boundary cannot be moved from inside the thing it bounds. This covers indirect routes — tool, prompt, connector and role changes — not only an explicit scope edit.
- **Disable logging, the audit trail or the human gate** — The only action whose success would hide every other action. Whoever can disable logging can usually suppress the policy event too, so the control path must live outside the agent's identity — a recorded event inside it is not sufficient evidence.
<!-- GENERATED:authority-rationales END -->

## Using it

Copy it, delete the rows that do not apply, and change the ones that do — then keep a note of what
you changed and why, because that note is the output of the exercise. Four rows are worth arguing
about first:

- **Executing an approved deletion rule is automatic; selecting records outside one needs
  approval — and the selector may not also execute.** Expired retention, confirmed erasure requests
  and de-duplication run on a schedule under a four-eyes-approved rule, with the selection criteria
  part of the approved rule version so the agent cannot widen the target set through a parameter.
  Two earlier versions got this wrong in opposite directions: first forbidding execution and so
  forbidding the compliant path, then forbidding the decision under a criterion it did not meet.
- **Revoking access is automatic; granting it needs approval.** Timely removal is a control, not a
  risk — putting a person in that path makes the organisation slower at the moment speed *is* the
  control.
- **Initiating a payment is approval, not refusal — but choosing the payee or the amount is
  refused.** Payment operations already run on separation of preparation, checking, approval and
  execution. An agent may occupy preparation and execution. What must not happen is the agent
  selecting the counterparty.
- **Classifying is automatic only while the label has no consequence.** Where a label drives
  credit, fraud, AML, HR or prioritisation outcomes, the label *is* the decision and belongs in
  the row below it.

## Open questions

- **A serious framework disagrees about the number of tiers.** SAFR — the industry white paper
  convened by the Monetary Authority of Singapore with HSBC, J.P. Morgan, Mastercard, Visa and
  OCBC — resolves every proposed action to *deny, escalate, auto-execute or observe*. This matrix
  has no equivalent of "observe": an action that proceeds and is looked at afterwards. The reason
  is recorded in `PD-AUTHORITY-001` along with what would change it, because a disagreement with
  work of that weight belongs in the open questions rather than in a footnote.
- **Nothing here says whether the evidence is read.** Every row names an artifact; no row says
  who looks at it or how often. "Automatic" therefore covers both "nobody looks" and "reviewed
  daily against thresholds" — a distinction the control levels do make and this table does not.
- The matrix is declared and rendered, not enforced. A check reconciling it against a running
  agent's declared action space would make the boundary testable rather than stated; it does not
  exist yet. Until it does, this documents an intent, and an evidence trail proves that something
  was logged — not that the access was authorised or the approval qualified.
- The preconditions are prose. Validation can check that a condition exists and applies to a
  plausible authority; it cannot check that the condition holds in a running system.
- Terms are used loosely on purpose and that has a cost. "Agent", "runtime", "scheduled process"
  and "competent person" are not defined here, and the deletion and payment rows lean on a
  decision/execution split that a deterministic executor called *by* the agent blurs.
- Rows describe a single agent. Delegation is one row, which is thin for a multi-agent system
  where the inherited scope is the whole question.
