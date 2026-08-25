# The whole thing, on one page

Four repositories, one job: **getting a concrete AI use case through a regulated organisation —
or stopping it — in a way that survives the second line, internal audit and a board.**

## The problem

An AI pilot works. Then it has to be approved, and the pilot team discovers that "it works" is
not a category anyone in the approval chain recognises. The second line asks for an audit
procedure, data protection asks for a deletion proof, outsourcing management asks for a
third-party classification, and the board asks what happens if it goes wrong. None of those are
answered by a better model.

The gap is not knowledge. Regulation is public and models can recite it. The gap is **the shape
of the evidence a regulated institution accepts** — and the fact that nobody publishes it,
because it is written under NDA or not written down at all.

## For whom

- **Second line and IT risk control** — need an audit procedure they can put in a test grid.
- **Internal audit** — need something they can lift into an audit programme.
- **Platform and AI leads** — need to know what will be asked before they are asked.
- **Boards and committees** — need a submission that states the residual risk and who owns it.

## What it is, precisely

**A decision support system, not a decision engine.** It structures the decision and produces the
evidence for it. It does not make it, and the distinction is load-bearing rather than modest:
what an obligation requires can be mapped and is; whether it applies to *your* system is a
case-by-case determination that no table can hold; how well you meet it is not scored, because a
single figure invites optimising the figure. That boundary is written down in
[what this maps, and what it does not](docs/00-scope/regulatory-scope.md), and every artifact here
respects it.

## What you actually get

| | |
|---|---|
| **[Risk and readiness rubrics](docs/02-risk-assessment/scoring-rubric.md)** | Six dimensions to a control level C1–C4, six more for whether the organisation can carry it. Deterministic, no model in the path. |
| **[Action authority matrix](docs/03-checklists/action-authority-matrix.md)** | What the agent may do alone, what a person approves, what is refused — every row with an evidence artifact. |
| **[Control catalogue](https://github.com/leonkoellerwirth-arch/rag-approval-blueprint)** | 23 RAG controls, each with an audit procedure in audit language, a named evidence artifact and a mapping to DORA, MaRisk and the GDPR. |
| **[Approval file](https://github.com/leonkoellerwirth-arch/rag-approval-blueprint)** | Eight parts, from protection requirement through to the board submission — as templates and as two worked cases. |
| **[Decision records](https://github.com/leonkoellerwirth-arch/rag-approval-blueprint/tree/main/decisions)** | Eighteen questions per use case, each answered at a reference the build resolves. Completeness is a number, not a claim. |
| **[Runtime enforcement](https://github.com/leonkoellerwirth-arch/local-agent-pipeline)** | Pre-action action-space whitelist, fail-safe human gate, hash-chained audit trail. A few hundred readable lines. |
| **[The gate](README.md#the-gate)** | The evaluator's exit codes as one command that writes JSON evidence. Runs offline; the CI action is optional. |

## Why it is useful

Because the artifacts are the ones the process actually consumes. An audit procedure that reads
like an audit procedure gets used; a control description that reads like marketing gets rewritten
by the person who has to use it, which is the same as not having it.

And because it says no. The portfolio contains a complete approval file for a system that was
**not** approved — eight red controls, three unhealable by any deadline, a board decision of no
approval, five conditions for resubmission. It stays refused, enforced by a test. A method that
only ever produces approvals has demonstrated nothing.

## What it deliberately is not

- **Not a platform.** No SaaS, no multi-tenant, no login, no database. One person cannot maintain
  a platform, and a half-finished one in a regulated environment is worse than none.
- **Not identity, inventory, inline filtering or drift detection.** Those are bought, they improve
  every quarter without us, and [competing there is choosing to lose slowly](docs/00-scope/what-this-does-not-build.md).
- **Not a maturity score.** No 0–100 index. The failure mode is documented: decommissioning your
  riskiest agent improves the number without improving one control.
- **Not legal advice, and not evidence of anyone's production use.** Every case here is fictional
  and labelled as such. See [`DISCLAIMER.md`](DISCLAIMER.md).

## The honest limits

The supervisory depth is German and EU financial. That is the strength and the ceiling: outside
that sector the control mappings are illustrative rather than authoritative. The register of
regulatory references still carries `owner_verified: false` — what has been checked and what has
not is listed in [`VERIFICATION.md`](VERIFICATION.md) rather than glossed. And one person
maintains all of it, which is why the scope is narrow on purpose.

---

*Reference implementation and illustrative cases — not production-tested, not a certification.*
