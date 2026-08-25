# Action authority matrix

What an agent may do on its own, what a named person approves first, and what is refused by
design. The scoring rubric answers how much control an agent needs; this answers the question a
reviewer asks immediately afterwards, and no rubric answers it: *so what is it allowed to do?*

**This enforces nothing.** It is a declared boundary, not a permission system — the thing an
implementation is measured against, and the thing an architect can disagree with in one reading.
The enforcing half is a pre-action check in the runtime; a reference implementation is
[`local-agent-pipeline`](https://github.com/leonkoellerwirth-arch/local-agent-pipeline), where the
action space is intersected before the worker ever sees a step.

Not legal advice — see [`DISCLAIMER.md`](../../DISCLAIMER.md).

## How to read it

| Column | Meaning |
|---|---|
| ✓ | Automatic. The agent may do this without asking, within its declared scope. |
| ✓ *< C3* | Automatic **below** that control level, human approval from that level up. |
| H | A named person approves this instance before it takes effect. |
| ✗ | Refused by design. The attempt is recorded and is itself a finding. |

`escalates_at` is the load-bearing idea. Few actions are categorically safe or categorically
forbidden; most are safe until the blast radius grows. The levels are the bands from
[`rubric.yaml`](../02-risk-assessment/scoring-rubric.md) — an escalation to a band that does not
exist fails the build rather than reading as a stricter rule than it is.

**Every row names an evidence artifact, including the forbidden ones.** A refusal that leaves no
trace cannot be audited, and an attempt to do a forbidden thing is a finding in its own right.

<!-- GENERATED:authority-matrix START — edit action_authority.yaml, then run `agent-eval render-docs` -->
### Reading

Actions that observe. They leak, they do not change.

| Action | Automatic | Human approval | Forbidden | Evidence |
|---|:---:|:---:|:---:|---|
| Search the internal knowledge base | ✓ | – | – | Query log with identity, query, retrieved document ids, timestamp |
| Retrieve records containing personal data | ✓ *< C3* | – | – | Query log plus the data categories touched, retained per the deletion concept |
| Read credentials, keys or secrets | – | – | ✗ | Policy event naming the attempted secret and the calling step |

### Producing

Actions that create something a human still has to act on.

| Action | Automatic | Human approval | Forbidden | Evidence |
|---|:---:|:---:|:---:|---|
| Draft a document, message or summary for a human | ✓ | – | – | Draft stored with model, prompt hash and output hash |
| Classify or tag a record without changing it | ✓ *< C4* | – | – | Decision log with input reference, label, confidence |

### Writing inside the boundary

Actions that change state the organisation controls.

| Action | Automatic | Human approval | Forbidden | Evidence |
|---|:---:|:---:|:---:|---|
| Write to its own scratch space or working store | ✓ | – | – | Change log for the working store |
| Modify customer, contract or master data | – | H | – | Change record with before/after values, approver identity and timestamp |
| Delete records | – | – | ✗ | Policy event naming the target and the calling step |
| Grant, change or revoke access rights | – | – | ✗ | Policy event naming the principal and the right requested |

### Acting on the outside world

Actions a third party observes. Rarely reversible by us alone.

| Action | Automatic | Human approval | Forbidden | Evidence |
|---|:---:|:---:|:---:|---|
| Send an email or message outside the organisation | – | H | – | Approval record linking approver, recipient, content hash and send timestamp |
| Initiate a payment or place a binding order | – | – | ✗ | Policy event naming the amount, counterparty and calling step |
| Publish content to a public channel | – | H | – | Approval record with the exact published artifact and its hash |
| Call an external API with organisational data | ✓ *< C3* | – | – | Call log with endpoint, data categories transmitted, provider and region |

### Acting on itself

Actions that change the agent's own scope, tools or oversight.

| Action | Automatic | Human approval | Forbidden | Evidence |
|---|:---:|:---:|:---:|---|
| Delegate a step to another agent | ✓ *< C3* | – | – | Trail entry naming the delegating step, the delegate and the inherited scope |
| Change its own action space, tools or policy | – | – | ✗ | Policy event naming the attempted change |
| Disable logging, the audit trail or the human gate | – | – | ✗ | Policy event; absence of trail entries is itself the alarm |
<!-- GENERATED:authority-matrix END -->

## Why each row is where it is

A matrix without reasoning is a preference. These are the arguments, and they are the part worth
disagreeing with.

<!-- GENERATED:authority-rationales START — edit action_authority.yaml, then run `agent-eval render-docs` -->
- **Search the internal knowledge base** — Reading within an identity-scoped index is the base case. It is automatic only while the authorisation check runs before retrieval, not after — filtering after the fact is a compensation, not a control.
- **Retrieve records containing personal data** — Reading is not harmless once the data is personal. From C3 the data_sensitivity dimension is what put the agent in that band, so the same reasoning applies to the read itself. Automatic below C3, human approval from there up.
- **Read credentials, keys or secrets** — An agent that can read a secret can exfiltrate it, and no downstream control recovers from that. Secrets reach tools through the runtime, never through the model's context.
- **Draft a document, message or summary for a human** — A draft has no effect until a person acts on it. The evidence is kept anyway, because the question later is not whether it was sent but what was proposed.
- **Classify or tag a record without changing it** — Harmless in isolation. At C4 classification usually feeds an automated consequence, and the classification is then the decision. Automatic below C4, human approval from there up.
- **Write to its own scratch space or working store** — The agent's own workspace is the one place it should be free. Anything it writes there is subject to the same review as anything else it produces.
- **Modify customer, contract or master data** — Master data is what other systems trust. A wrong value propagates silently and is found weeks later by someone who cannot tell where it came from.
- **Delete records** — Deletion is the one action whose evidence deletion destroys. Retention and erasure run through the deletion concept, on a schedule, with a proof — never through an agent decision.
- **Grant, change or revoke access rights** — An agent that can widen its own reach has no boundary. This stays with the joiner-mover- leaver process regardless of control level.
- **Send an email or message outside the organisation** — The first action in this matrix a third party observes. Recall is not a control; the recipient has already read it.
- **Initiate a payment or place a binding order** — Moving money is the rubric's own categorical override: action_space at its maximum forces C4 regardless of the total. Forbidden here rather than escalated, because an approval workflow around a payment agent is a payment agent.
- **Publish content to a public channel** — Publication is irreversible in the only sense that matters: it has been seen. The evidence must be the artifact itself, not a description of it.
- **Call an external API with organisational data** — Routine for read-only enrichment, and a third-party transfer once the data is personal or confidential. The evidence must name the region, because the contractual question is asked about where processing happened, not about which library was called. Automatic below C3, human approval from there up.
- **Delegate a step to another agent** — Delegation is where an action space quietly widens: the child must not exceed the parent. From C3 the chain has to be visible to a reviewer, not merely present in a log. Automatic below C3, human approval from there up.
- **Change its own action space, tools or policy** — The boundary cannot be inside the thing it bounds. Scope changes are a deployment, reviewed as one.
- **Disable logging, the audit trail or the human gate** — The only action whose success would hide every other action. This is why the gate is evaluated outside the agent's reach and the trail is tamper-evident rather than merely append-only.
<!-- GENERATED:authority-rationales END -->

## Using it

Copy the file, delete the rows that do not apply, and change the ones that do — then keep the
changed rows, because the disagreements are the useful part of the exercise. An organisation that
adopts this unchanged has not thought about it.

Three rows are worth arguing about before anything else:

- **Initiating a payment is forbidden here, not escalated.** An approval workflow wrapped around
  a payment agent is a payment agent. If your organisation escalates it instead, write down what
  the approver actually sees at the moment of approval.
- **Deleting records is forbidden at every level.** Deletion is the one action whose evidence its
  own success destroys. Retention and erasure belong to a scheduled process with a proof.
- **Reading personal data escalates at C3 rather than being forbidden or free.** Reading is not
  harmless once the data is personal, and it is not a decision either.

## Open questions

- The matrix is declared and rendered, not enforced. A check that reconciles it against a running
  agent's declared action space would make the boundary testable rather than stated; that check
  does not exist yet.
- Rows are written for a single agent. Delegation is covered by one row, which is thin for a
  multi-agent system where the inherited scope is the whole question.
