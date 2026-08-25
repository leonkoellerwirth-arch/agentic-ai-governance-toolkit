# What this maps, and what it does not

Read this before the checklists.

Across these repositories, three things that look alike are treated very differently. Stating the
difference once, here, is cheaper than defending it three times — and it is the difference on which
everything else in this toolkit depends.

| | Question | Answer |
|---|---|---|
| **1. Obligation** | What does the article require? | Mapped. Quotable, pinned to a consolidated version. |
| **2. Application** | Does it apply to *this* system? | Not mapped. Case-by-case determination. |
| **3. Attainment** | How well does the organisation meet it? | Not scored. No index is produced. |

---

## 1. What an article requires — mapped

The record-keeping obligation for high-risk systems — row 4.1 of the
[EU AI Act checklist](../03-checklists/eu-ai-act-agent-checklist.en.md) — says what it says. It can
be quoted, pinned to a consolidated version, and tested against drift.

This document cites no article numbers of its own, by the same rule the reference checker enforces
on every prose document here: a bare article number means different things in different acts, so it
belongs in a document bound to exactly one framework. The checklists are those documents.

This is what [`regulatory_sources.yaml`](../../evaluator/src/agent_evaluator/regulatory_sources.yaml)
holds, and it is the only layer this toolkit claims to have mapped. Every article reference in every
checklist resolves to an entry there, with a CELEX identifier, an OJ citation, a version and a URL.
A test fails if a checklist cites an article the register does not carry.

The register is a bibliography with structure. It is not an interpretation.

## 2. Whether it applies to a given system — not mapped

Whether a particular internal assistant is a high-risk system — see rows 1.2 and 1.3 of the
[EU AI Act checklist](../03-checklists/eu-ai-act-agent-checklist.en.md) — is a determination against
the deployment context, the role in the value chain, the sector and the actual function. Two systems
with identical architecture can land on opposite sides of it.

No table holds that. A table that appeared to hold it would be read as holding it, which is worse
than not having one.

This is why [`rag-approval-blueprint`](https://github.com/leonkoellerwirth-arch/rag-approval-blueprint)
maps DORA, MaRisk and the GDPR for its 23 controls but declines to map the AI Act: the DORA and
MaRisk obligations attach to the institution, which is already known. The AI Act obligations attach
to a classification that has to be determined first. Declining to map it is not a gap in that
repository. It is the same position as this section, applied.

## 3. How well an organisation meets it — not scored

The readiness rubric produces required, achieved and met per dimension, and the gaps between them.
It does not produce a single figure. The reason is recorded with the decision, not asserted here:
a single number invites optimising the number.

The failure mode is concrete and documented — decommissioning the single riskiest agent lowers
reported exposure, and every dimension measured against it, without one control having improved.
The rubric names that in its own output rather than hiding it.

[`platform-decision-kit`](https://github.com/leonkoellerwirth-arch/platform-decision-kit) goes one
step further and carries no regulatory checklist at all, on the grounds that a checklist inside a
discovery instrument would be read as an assessment. Same distinction, one layer earlier.

---

## Where triage sits

`agent-eval score`, and any classification tool built on the same rubric, sit between question 1 and
question 2 — and that position has to be stated in the output, not only here.

What they do: structure the input to a determination. Which dimensions matter, what a defensible
answer to each looks like, which controls the resulting band implies, and which questions are still
open.

What they do not do: make the determination. A control level of C4 is a statement about what the
system can do, not a finding that it is high-risk within the meaning of the classification rules.

The practical rule for anything built on this rubric — a command, a skill, an MCP tool, a report:
**the output says what it is.** "Heuristic pre-assessment, not a classification" belongs in the
response payload, where someone acting on it will see it, not in a document they will not open.

## Verification status

`regulatory_sources.yaml` carries an `owner_verified` flag. While it is `false`, the article
references have been recorded and pinned but not read back against the original text by a person.

That is a legitimate interim state and an illegitimate resting state. Anything built on the register
inherits its verification status, and a tool that circulates an unverified reference circulates it
faster than it can be corrected.

## Dated obligations

Two dates are already known and are maintenance appointments, not opinions:

- **BAIT (Circular 10/2017 BA)** is withdrawn in full as of 31 December 2026. From January 2027,
  every BAIT reference needs an explanation. `rag-approval-blueprint` already marks its BAIT
  mappings as historical for this reason.
- Regulatory change is an incident, not maintenance. When an obligation changes, that is a release
  with a changelog and a version bump — never a silent commit.

## How to cite this

When a document in any of these repositories maps an obligation, it is making the claim in
section 1 and no other. If it appears to make the claim in section 2 or 3, that is a defect in
the document; report it.

None of this is legal advice — see [`DISCLAIMER.md`](../../DISCLAIMER.md).

## Open questions

- `owner_verified` is `false` at the time of writing. The count of references and the date of the
  last verification pass belong in this section once that pass has been run.
- The boundary in "Where triage sits" is stated but not yet enforced by a test. A check that every
  tool output carrying a control level also carries its scope disclaimer would make it structural
  rather than editorial.
- Whether the MaRisk 9. Novelle (June 2026) affects the existing mappings has not been assessed.
