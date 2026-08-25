# Reference architecture

Where the model sits, where the boundary is, and where the evidence comes from. One picture for
the questions an architect asks before reading any control catalogue, and a table underneath
because a diagram alone answers none of them precisely.

The authority markers match the [action authority matrix](../03-checklists/action-authority-matrix.md):
**[A]** automatic, **[A\*]** automatic while its preconditions hold, **[H]** human approval,
**[X]** refused by design.

Illustrative reference architecture, not a deployed system. Not legal advice — see
[`DISCLAIMER.md`](../../DISCLAIMER.md).

```mermaid
flowchart LR
    subgraph people["People"]
        REQ["Requester"]
        APP["Approver<br/>or responsible function"]
    end

    subgraph org["Organisational trust boundary"]
        subgraph identity["Identity"]
            IDB["Delegation broker<br/>issues a scoped, time-bound,<br/>audience-bound token"]
        end

        subgraph control["Control plane — deterministic, no model in the path"]
            POL["Action policy<br/>(authority matrix)"]
            CHK["Pre-action check<br/>intersect requested action<br/>with the action space"]
            GATE["Human gate<br/>fail-safe: reject"]
            TRAIL[("Audit trail<br/>append-only, hash-chained")]
        end

        subgraph runtime["Agent runtime — sees model output"]
            PLAN["Planner"]
            WORK["Worker"]
            REV["Reviewer"]
        end

        subgraph brokers["Brokers — fixed schemas, no model output admitted"]
            TOOL["Tool and secret broker<br/>capability-bound, sink-side checks"]
        end

        subgraph data["Data plane"]
            IDX[("Vector index<br/>self-operated")]
            SOR[("Systems of record")]
            SEC[("Secret store")]
        end
    end

    subgraph outside["Outside the boundary"]
        LLM["Model inference<br/>provider, region recorded"]
        API["Third-party API"]
        RCP["External recipient"]
    end

    REQ --> IDB
    IDB -->|"scoped token"| PLAN
    PLAN -->|"every step"| CHK
    POL --> CHK
    CHK -->|"[A] within the action space"| WORK
    CHK -->|"[X] outside it — step discarded"| TRAIL
    WORK -->|"[A*] authorisation before retrieval;<br/>[H] special category, bulk, exception"| IDX
    IDX --> WORK
    SOR --> WORK
    WORK -->|"prompt and output hashes,<br/>provider and region"| TRAIL
    WORK <-->|"inference"| LLM
    WORK -->|"tool request — never a secret"| TOOL
    TOOL --> SEC
    TOOL -->|"[A*] approved flow, provider, region"| API
    TOOL -->|"[A*] approved deletion rule;<br/>[A*] revocation on a source event"| SOR
    TOOL -->|"[A*] pre-approved template, recipient from the record"| RCP
    WORK -.->|"[X] never reaches the model context"| SEC
    WORK --> REV
    REV -->|"escalate"| GATE
    WORK -->|"[H] record change, composed message, payment"| GATE
    GATE --> APP
    APP -->|"approve · reject · edit"| GATE
    GATE -->|"[H] approved"| TOOL
    PLAN --> TRAIL
    REV --> TRAIL
    GATE --> TRAIL
    TOOL --> TRAIL

    classDef refused stroke-dasharray: 4 3
    class SEC refused
```

[Source](diagrams/agent-reference-architecture.mmd) · [SVG](diagrams/agent-reference-architecture.svg)

## The questions, answered

| Question | Answer in this architecture |
|---|---|
| Where does the model sit? | Outside the boundary, at an inference provider whose region is recorded per call. Nothing here assumes it is trustworthy, and the provider writes to its own logs, not to this trail. |
| Where does retrieval sit? | Inside. Index and embeddings are self-operated, which is what makes a deletion proof possible at all. |
| Where do tools sit? | Behind a broker with fixed schemas that admits no model output as an instruction. The worker asks the broker for an effect; it never holds the credential. |
| Which identity is used? | A scoped, time-bound, audience-bound delegation token issued by the broker before any step runs. Retrieval *verifies* that token — it does not establish identity, and drawing it as if it did was the first version's mistake. |
| Which systems may be read? | The index and systems of record, with authorisation evaluated **before** retrieval. Special-category data, bulk access and exceptional purposes escalate — retrieval is `[A*]`, not `[A]`. |
| Which systems may be written? | Systems of record. Two paths are automatic under preconditions: executing an approved deletion rule, and revoking access on a source event. Everything else goes through the gate. |
| What needs human approval? | Composed messages leaving the organisation, ad-hoc record changes, payments, and anything the reviewer escalates. |
| What is refused outright? | Reading secrets into the model context, changing the agent's own scope, disabling oversight — each under a named limb of the refusal criterion. |
| What may happen automatically? | Retrieval inside the action space, drafting, calls inside an already-approved flow, and pre-approved templated notifications where the recipient comes from the record. |
| Which data is processed outside? | Whatever the prompt carries to the provider, plus whatever an approved third-party call transmits — both logged with data categories and region. |
| Where do logs arise? | Planner, worker, reviewer, gate and broker each write to one append-only, hash-chained trail. Hashes bind content that is already known; they do not prove the access was authorised or that no event was omitted. |

## The two boundaries that matter

**The organisational boundary** is the outer box. Data crossing it is a transfer, and the
architecture is arranged so that crossings are few, named and logged with their region. The model
is on the far side of it, which is the single most consequential fact in the picture.

**The control-plane boundary** is the inner one, and it is the less obvious of the two. Policy,
the pre-action check, the gate and the trail sit outside the agent's reach — no model in the path,
nothing the agent can widen from inside. This is why refusing to *disable oversight* is a
meaningful row rather than a wish: if the control plane were inside the runtime, an agent that
could stop logging could also suppress the record of having stopped it.

## What this diagram does not show

- **It is a reference, not a deployment.** No real system is drawn here, and a real one will differ
  in the places that matter most to it.
- **It shows one agent.** Delegation appears in the matrix as a row and not in the picture; a
  multi-agent topology, where inherited scope is the whole question, needs its own diagram.
- **Arrows are permissions, not guarantees.** The picture shows where a check *is placed*, not that
  it is effective. A pre-action check drawn in the right place and implemented in the wrong one
  looks identical here.
- **Hashes are not proof of the act.** They bind content already known to whoever holds it. They do
  not establish that an access was authorised, that a decision was competent, or that no event was
  left out. The trail's value is that tampering with what *was* recorded is detectable — not that
  the record is complete.
- **No failure paths.** Timeouts, partial writes, retries and compensating actions are where real
  incidents live, and none of them are drawn.

## Open questions

- The trail is drawn as one store. In practice, planner, gate and provider calls often land in
  different systems with different retention, and reconciling them is work the picture hides.
- Nothing here shows *when* the architecture is re-examined. An architecture diagram without a
  review trigger becomes a description of the past, and the trigger belongs in the operating model
  rather than in the drawing.
