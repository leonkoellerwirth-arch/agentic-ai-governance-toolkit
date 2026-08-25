# Regulatory sources — the source lock

Every article reference in the checklists points at a specific act, in a specific version, checked
on a specific date. This page is that record, generated from
[`regulatory_sources.yaml`](../../evaluator/src/agent_evaluator/regulatory_sources.yaml) — the
single source of truth. A test fails if a checklist cites an article this page does not carry, or
if this page carries one no checklist cites.

> **Why this page exists.** An article number on its own does not say which version it was written
> against, and EU acts get amended. A reference marked "verify" is only useful if you know *what* to
> verify against. This page answers that, and nothing more.
>
> Article references live **only in the checklists**, which are each bound to one framework here —
> a bare article number means different things in different acts. Every other document points at a
> checklist row instead, and a test fails if one starts citing articles on its own.

> **What this page deliberately does not contain:** deadlines, application dates, penalties, or any
> statement about what an obligation requires of you. Those are legal conclusions. This is a
> practitioner's toolkit, not legal advice — it records **provenance**, so that you and your counsel
> can check the rest against the real text.

## The acts

<!-- GENERATED:registry START — edit regulatory_sources.yaml, then run `agent-eval render-docs` -->
### EU AI Act — Regulation (EU) 2024/1689

| Field | Value |
|---|---|
| CELEX | `32024R1689` |
| Official Journal | OJ L, 2024/1689, 12.7.2024 |
| Version checked | consolidated text 02024R1689-20260727, as of 2026-07-27 |
| Text | [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727) |

**Amendments incorporated**

- **Regulation (EU) 2026/1744** — CELEX 32026R1744, OJ L, 2026/1744, 24.7.2026, in force 2026-07-27. Digital Omnibus on AI. It moves application dates: the high-risk obligations for standalone systems now apply from 2 December 2027, and for high-risk AI embedded in products already covered by Union product legislation from 2 August 2028. The transparency obligations and the AI-literacy duty are unchanged. Which dates bind you is a legal question this toolkit does not answer — but a checklist read without this note reads as if every row below were already in force.

**Referenced in the checklists**

| Article | Subject as the checklist names it |
|---|---|
| 5 | prohibited practices |
| 6 | high-risk classification |
| annex-III | high-risk classification list |
| 9 | risk management (high-risk) |
| 10 | data governance (high-risk) |
| 11 | technical documentation (high-risk) |
| annex-IV | technical documentation contents |
| 12 | record-keeping (high-risk) |
| 13 | instructions for use (high-risk) |
| 14 | human oversight (high-risk) |
| 15 | accuracy, robustness and cybersecurity (high-risk) |
| 50 | transparency obligations |
| 51-55 | general-purpose AI model obligations |
| 72 | post-market monitoring system (high-risk) |
| 73 | reporting of serious incidents (high-risk) |

### DORA — Regulation (EU) 2022/2554

| Field | Value |
|---|---|
| CELEX | `32022R2554` |
| Official Journal | OJ L 333, 27.12.2022, pp. 1–79 |
| Version checked | as of 2022-12-27 |
| Text | [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554) |

**Amendments incorporated**

- None recorded.

**Referenced in the checklists**

| Article | Subject as the checklist names it |
|---|---|
| 5-6 | ICT risk management framework |
| 9 | protection and prevention |
| 10 | detection |
| 11 | response and recovery |
| 12 | backup and restoration |
| 17 | ICT-related incident management process |
| 18 | classification of ICT-related incidents |
| 19 | reporting of major ICT-related incidents |
| 24-27 | digital operational resilience testing |
| 28 | ICT third-party risk |
| 30 | key contractual provisions |
<!-- GENERATED:registry END -->

## How these entries were checked

<!-- GENERATED:verification START — edit regulatory_sources.yaml, then run `agent-eval render-docs` -->
Checked on **2026-08-14** — fetched from EUR-Lex and read off the document metadata. Entries are **not yet** confirmed by eye against the sources below.

- <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689>
- <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727>
- <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32026R1744>
- <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554>

Commentary — law-firm notes, news articles, summaries, AI-generated review — is never the source of an entry here. Several articles repeating one Official Journal publication are one source, not several.
<!-- GENERATED:verification END -->

## Keeping it current

When an act is amended, or when you adopt this toolkit in your own organization:

1. Open the EUR-Lex link for the framework and read the current consolidated version.
2. Update `consolidated_as_of`, `consolidated_celex`, and `amended_by` in
   `regulatory_sources.yaml`. Record the date of the check in `verification.verified_at`.
3. Run `agent-eval render-docs`. Every checklist header updates from this one edit.
4. Re-read the checklist rows the amendment touches. A source lock records which text applies; it
   does not tell you whether the checklist still says the right thing about it.

Step 4 is the one that cannot be automated, and the one that matters.
