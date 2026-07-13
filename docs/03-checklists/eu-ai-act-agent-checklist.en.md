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

---

*Article references are indicative and must be verified against the current consolidated text of
Regulation (EU) 2024/1689 and its implementing acts. This checklist does not establish compliance.*
