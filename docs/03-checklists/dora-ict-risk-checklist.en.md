# DORA — ICT-risk checklist for AI agents

A working checklist that looks at an AI agent through the lens of **ICT risk management** under the
Digital Operational Resilience Act (DORA, Regulation (EU) 2022/2554). An agent — especially one that
calls an external LLM API — is an ICT asset and often an ICT third-party dependency; DORA's
resilience discipline applies to it like any other.

> **This is a practitioner's toolkit, not legal advice.** DORA applies to defined financial entities
> and is subject to proportionality. Whether a specific obligation binds you, and how, depends on
> your entity type and the arrangement. Treat article references as **indicative pointers to verify
> against the current legal text** and the relevant RTS/ITS. There is a German version:
> [`dora-ict-risk-checklist.de.md`](dora-ict-risk-checklist.de.md).

Fill the **Status** column with ✓ (done), ✗ (open), or n/a.

## 1. ICT risk management and inventory

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 1.1 | The agent is recorded in the **ICT asset inventory**, mapped to the business function it supports (ICT risk management framework, Art. 5–6 — verify). | Inventory entry | IT operations | ☐ |
| 1.2 | Its **dependencies** are documented — models, data stores, external APIs, orchestration. | Architecture / dependency map | AI team | ☐ |
| 1.3 | The agent is mapped to a **criticality / impact tolerance** for the function it serves. | Business-impact record | Business (1st line) | ☐ |
| 1.4 | **Protection and prevention** controls (access, segregation, least privilege on the action space) are in place (Art. 9 — verify). | Control design | AI team | ☐ |

## 2. Detection and monitoring

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 2.1 | Anomalous agent behaviour is **detected** through monitoring and thresholds (Art. 10 — verify). See [KPI catalog](../05-monitoring/kpi-catalog.md). | Monitoring config | IT operations | ☐ |
| 2.2 | The agent emits an **audit trail** adequate for detection and forensics. See [logging requirements](../05-monitoring/logging-requirements.md). | Log sample | AI team | ☐ |

## 3. Response, recovery, and resilience testing

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 3.1 | **Failure scenarios** are defined and rehearsed: model/API unavailable, degraded output, timeout, rate-limit, wrong-but-confident output (response & recovery, Art. 11 — verify). | Scenario playbook | AI team | ☐ |
| 3.2 | A **fallback** for provider or model outage is defined (graceful degradation, queue-and-hold, or human handover). | Design doc | AI team | ☐ |
| 3.3 | **Backup and restoration** for the agent's state and configuration is defined and tested (Art. 12 — verify). | Backup test record | IT operations | ☐ |
| 3.4 | The agent is included in **resilience testing** proportionate to its criticality (digital operational resilience testing, Art. 24–27 — verify). | Test plan/results | IT operations | ☐ |

## 4. ICT third-party risk — external model and API providers

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 4.1 | Any **external LLM/API provider** is recorded as an ICT third-party arrangement in the register of information (ICT third-party risk, Art. 28 — verify). | Third-party register | Procurement / Risk | ☐ |
| 4.2 | The **contract** covers the provisions DORA expects — access, audit, sub-outsourcing, service levels, termination, incident cooperation, data location (Art. 30 — verify). | Contract clauses | Legal / Procurement | ☐ |
| 4.3 | **Concentration and exit** risk is assessed — what happens if this provider fails or must be replaced. | Exit plan | Risk (2nd line) | ☐ |
| 4.4 | Data sent to the provider is **classified and minimized**; personal or special-category data handling is documented. | Data-flow record | AI team | ☐ |

## 5. Incident management and reporting

| # | Criterion | Evidence | Responsible | Status |
|:-:|-----------|----------|-------------|:------:|
| 5.1 | An **incident management process** covers agent incidents — detection, handling, escalation (Art. 17 — verify). | Incident process | IT operations | ☐ |
| 5.2 | Agent incidents are **classified** against your criteria for major ICT-related incidents (Art. 18 — verify). | Classification record | Risk (2nd line) | ☐ |
| 5.3 | **Reporting paths** for major incidents are known and rehearsed (Art. 19 — verify). | Escalation / reporting plan | Risk (2nd line) | ☐ |

---

*Article references are indicative and must be verified against the current text of Regulation (EU)
2022/2554 and the relevant RTS/ITS. This checklist does not establish compliance.*
