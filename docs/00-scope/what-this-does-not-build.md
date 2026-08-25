# What this does not build, and what does

Stand: 25 August 2026. Product facts are as published on that date and are worth re-checking
before you rely on them; this file is not maintained as market research.

Most of what an AI governance programme needs is bought, not written. This repository is written
by one person, and the only defensible reason for it to exist is that it does a narrow thing the
platforms do not. Naming the boundary is more useful to a reader than a feature list — it tells
them what to buy, and it tells them what they still cannot buy.

## The short version

| Capability | Covered by | Built here |
|---|---|---|
| Agent identity, least privilege, entitlements | Microsoft Entra Agent ID / Agent 365 | no |
| Organisation-wide agent registry and inventory | Microsoft Agent 365, Credo AI, IBM watsonx.governance | no |
| Runtime content filtering, PII redaction, grounding checks | AWS Bedrock Guardrails, Google Vertex AI | no |
| Policy packs for EU AI Act, NIST AI RMF, ISO 42001, SOC 2, NYC LL 144 | Credo AI (also resold by IBM) | no |
| Statistical fairness and bias assessment | Holistic AI, Fairly AI, Credo AI | no |
| Continuous model monitoring, drift detection | IBM watsonx.governance | no |
| SIEM integration, tenant-wide policy enforcement | Microsoft Purview / Defender | no |
| **Controls mapped to DORA, MaRisk and the GDPR, with audit procedures in the language a German internal-audit function writes in** | — | **yes** |
| **A worked approval file that ends in a refusal, kept refused** | — | **yes** |
| **A board submission and an audit programme as artifacts, not as descriptions** | — | **yes** |
| **Open-source runtime enforcement you can read: pre-action whitelist, human gate, hash-chained trail** | — | **yes** |

## What the platforms already do well

**Microsoft** treats an agent as an identity. Entra Agent ID and Agent 365 give each agent an
identity, scoped permissions, an owner and time-bound access, with a registry that inventories
Microsoft and non-Microsoft agents alike, activity auditing through Purview and isolated
execution. The Entra admin-centre registry was retired on 1 May 2026 and converged into Agent
365. If your problem is *which agents exist and what may they reach*, this is the layer to buy.

**Credo AI** is the closest thing to this repository as a product, and it is further along.
Policy packs translate the EU AI Act, NIST AI RMF, ISO 42001, SOC 2 and NYC Local Law 144 into
control sets with evidence requirements; the registry covers systems, third-party AI and agents;
GAIA, its governance agent, reached general availability in May 2026 and automates documentation,
risk identification and control mapping. IBM resells those policy packs as an accelerator for
watsonx.governance, which says something about the depth of the underlying library.

**IBM** brings structured intake, per-use-case risk assessment, continuous monitoring of deployed
agents and red-teaming. **AWS** and **Google** operate one layer lower: inline screening in front
of the model — content filtering, PII detection, grounding checks. Useful, and not an approval
process.

**Holistic AI** and **Fairly AI** cover fairness and bias assessment with EU AI Act coverage.

## Where the remaining gap is

Everything above is horizontal. What none of it does, as far as their public material shows, is
the German and EU financial-supervisory layer — **DORA, MaRisk and BAIT** — and the artifacts
that layer is actually consumed as.

That gap is narrow on purpose, and it is where this repository and its siblings sit:

**Controls carrying supervisory references.** Twenty-three RAG controls in
[`rag-approval-blueprint`](https://github.com/leonkoellerwirth-arch/rag-approval-blueprint), each
with an objective, an audit procedure written the way an internal-audit function writes one, a
named evidence artifact and a mapping to DORA, MaRisk and the GDPR. A policy pack tells you an
obligation exists. It does not tell your second line what to ask for and what to accept as proof.

**A refusal that stays refused.** A complete approval file for a system that did *not* get
approved: eight red controls, three of which no deadline can heal, a board decision of no
approval, and five conditions for resubmission. Vendors publish successes. A method that only
ever produces approvals has demonstrated nothing.

**Board and audit artifacts.** A submission with a resolution, a documented dissenting opinion,
an audit programme and an audit report. Not a dashboard describing that governance happened —
the documents that go into the file.

**Enforcement you can read.** [`local-agent-pipeline`](https://github.com/leonkoellerwirth-arch/local-agent-pipeline)
is a reference implementation, not a product: the action space is intersected before the worker
sees a step, the human gate fails safe to reject, and the audit trail is a hash chain with an
optional HMAC seal. Every platform above enforces as a service. This one enforces in a few
hundred lines you can read in an afternoon and disagree with.

## The rule this follows

Build only what stays true when the platforms improve. Identity, inventory, inline filtering and
drift detection all get better every quarter without us; competing there as one person is
choosing to lose slowly. Supervisory depth and a documented refusal do not commoditise, because
they are not features — they are the residue of having done the work.

Everything in the "no" column above is a decision, not an omission. If a reader needs it, the
answer is to buy it, and this file is the recommendation to do so.

## Open questions

- Product capabilities move faster than this file. It carries a date rather than a promise; treat
  a claim older than a quarter as a starting point for your own check, not as a finding.
- The claim that no vendor covers DORA and MaRisk at control level rests on public product
  material. A vendor may cover it in a customer-specific policy pack that is not published.
- No pricing comparison is attempted. For most organisations the honest answer is a platform for
  breadth and this repository for the supervisory layer, not one instead of the other.
