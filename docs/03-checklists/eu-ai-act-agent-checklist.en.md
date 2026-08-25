# EU AI Act — checklist for AI agents

A working checklist for teams putting an AI agent into a regulated organization. It focuses on the
themes that matter most for **agents** — risk classification, transparency, human oversight, and
logging/documentation — and points to where each maps in the EU AI Act (Regulation (EU) 2024/1689).

> **This is a practitioner's toolkit, not legal advice.** Whether — and how — a specific obligation
> applies depends on your system's risk classification, your role (provider, deployer, …), and the
> facts of the use case. Treat the article references as **indicative pointers to verify against the
> current legal text**, not as a determination that an obligation applies. Confirm with qualified
> counsel and your compliance function. There is a German version:
> [`eu-ai-act-agent-checklist.de.md`](eu-ai-act-agent-checklist.de.md).

<!-- GENERATED:source_lock START — edit regulatory_sources.yaml, then run `agent-eval render-docs` -->
> **Source lock.** The article references below point at **Regulation (EU) 2024/1689** (CELEX 32024R1689, OJ L, 2024/1689, 12.7.2024) — consolidated text 02024R1689-20260727, as of 2026-07-27.
> Amended by **Regulation (EU) 2026/1744** (CELEX 32026R1744, OJ L, 2026/1744, 24.7.2026), in force 2026-07-27.
> Digital Omnibus on AI. It moves application dates: the high-risk obligations for standalone systems now apply from 2 December 2027, and for high-risk AI embedded in products already covered by Union product legislation from 2 August 2028. The transparency obligations and the AI-literacy duty are unchanged. Which dates bind you is a legal question this toolkit does not answer — but a checklist read without this note reads as if every row below were already in force.
> Last checked against the text on 2026-08-14: [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727). Pinned in [`regulatory-sources.md`](regulatory-sources.md).
> This records **which text**, not what it requires of you.
<!-- GENERATED:source_lock END -->

Fill the **Status** column with ✓ (done), ✗ (open), or n/a. Record where the evidence lives.

## 1. Classification — what kind of AI system is this?

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 1.1 | The agent has been checked against the **prohibited practices** and is not one of them (EU AI Act, Art. 5 — verify). | Triage note | Risk (2nd line) | ☐ |
| 1.2 | The agent's **risk category** has been determined (high-risk per Art. 6 / Annex III, transparency-risk, or minimal), with reasoning. | Classification record | Risk (2nd line) | ☐ |
| 1.3 | Your **role** in the value chain (provider / deployer / distributor) is identified, because obligations differ by role. | Classification record | Risk (2nd line) | ☐ |
| 1.4 | If the agent builds on a **general-purpose AI model**, the associated obligations are considered (Art. 51–55 — verify). | Model inventory | AI team | ☐ |

## 2. Transparency

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 2.1 | People who **interact with the agent** are informed they are dealing with an AI, where required (transparency obligations, Art. 50 — verify). | UX copy / disclosure | AI team | ☐ |
| 2.2 | **AI-generated or manipulated content** the agent produces is marked/disclosed where required. | Output labelling | AI team | ☐ |
| 2.3 | Deployers receive the **information and instructions** they need to use the agent correctly (Art. 13 for high-risk — verify). | Instructions for use | Provider | ☐ |

## 3. Human oversight

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 3.1 | The agent's autonomy is bounded by a defined **action space**; actions outside it are refused. | Design doc | AI team | ☐ |
| 3.2 | **Human oversight** is designed in proportionate to risk — a human can review, intervene, and stop the agent (Art. 14 for high-risk — verify). | HITL design | AI team | ☐ |
| 3.3 | For higher control levels (C3–C4), in-scope actions require an **explicit human approve/reject** or per-action authorization. | Control design | Risk (2nd line) | ☐ |
| 3.4 | A **kill-switch / stop** procedure exists and has been tested. | Runbook + test record | IT operations | ☐ |

## 4. Logging, record-keeping, and documentation

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 4.1 | The agent keeps an **audit trail** of its decisions and actions sufficient to reconstruct what happened (record-keeping, Art. 12 for high-risk — verify). See [logging requirements](../05-monitoring/logging-requirements.md). | Log sample | AI team | ☐ |
| 4.2 | **Technical documentation** of the agent, its data, and its controls is maintained (Art. 11 / Annex IV for high-risk — verify). | Tech doc | AI team | ☐ |
| 4.3 | **Data governance** for training/reference data is addressed — provenance, quality, and personal-data handling (Art. 10 for high-risk — verify). | Data governance record | AI team | ☐ |
| 4.4 | **Accuracy, robustness, and cybersecurity** are tested proportionate to risk (Art. 15 for high-risk — verify). | Test evidence | AI team | ☐ |

## 5. Governance around the agent

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 5.1 | A **risk management** approach covers the agent across its lifecycle (Art. 9 for high-risk — verify). | Risk assessment | Risk (2nd line) | ☐ |
| 5.2 | An **accountable owner** is named and recorded in the agent registry. | Registry entry | Business (1st line) | ☐ |
| 5.3 | **Re-assessment** is scheduled and triggered by material change (model, autonomy, data, action space). | Re-assessment plan | Risk (2nd line) | ☐ |

## 6. Incidents and life after go-live

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 6.1 | What counts as a **serious incident** for this agent is defined, and the monitoring to notice one is in place (reporting of a serious incident, Art. 73 for high-risk — verify). See [incident response](../05-monitoring/incident-response.md). | Incident definition | Risk (2nd line) | ☐ |
| 6.2 | **Reporting paths** are named, time-bound, and have been walked through — not only written down (Art. 73 — verify). | Reporting plan + rehearsal record | Risk (2nd line) | ☐ |
| 6.3 | **Post-market monitoring** of the agent in real use feeds back into re-assessment (post-market monitoring system, Art. 72 for high-risk — verify). See [KPI catalog](../05-monitoring/kpi-catalog.md). | Monitoring plan | AI team | ☐ |
| 6.4 | **Provider and model dependency** is recorded, and a provider-side change triggers re-assessment. See [provider dependency](../04-operating-model/provider-dependency.md). | Registry entry | AI team | ☐ |

---

*Article references are indicative and must be verified against the current consolidated text of
Regulation (EU) 2024/1689 and its implementing acts. This checklist does not establish compliance.*
