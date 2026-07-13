# Use-case intake form

The triage form for a new agent use case (lifecycle phase 1). Fill it in, then run
[risk assessment](../docs/02-risk-assessment/agent-risk-model.md). Copy this file per use case.

> This is a practitioner's toolkit, not legal advice.

## 1. Basics

- **Use-case name:**
- **Requesting business unit:**
- **Proposed accountable owner (1st line):**
- **Date / intake reference:**

## 2. What should the agent do?

- **Problem / value in two sentences:**
- **What the agent does (task):**
- **What stays with a human:**

## 3. Is this an agent? (triage)

- [ ] The system **acts or decides**, not just retrieves/summarizes.
- [ ] It has some **autonomy** (it can take a step without a human confirming each one).
- [ ] It can **affect systems or the outside world**.

> If none are checked, this is likely classic software — govern it through your standard SDLC and
> stop here.

## 4. Scope and dependencies

- **Systems it reads from:**
- **Systems it writes to:**
- **External model/API providers (if any):**
- **Data categories it touches:** ☐ public ☐ internal ☐ personal ☐ special-category / secrets

## 5. Prohibited-use screen

- [ ] Checked against prohibited/unacceptable uses (see
  [EU AI Act checklist §1](../docs/03-checklists/eu-ai-act-agent-checklist.en.md)). **Not** prohibited.
- Notes:

## 6. Initial risk self-assessment (1–5 each)

Provisional — Risk (2nd line) confirms in phase 2. See the
[risk model](../docs/02-risk-assessment/agent-risk-model.md).

| Dimension | Score (1–5) | Note |
|-----------|:-----------:|------|
| Autonomy | | |
| Action space | | |
| Reversibility | | |
| Data sensitivity | | |
| Explainability | | |
| Blast radius | | |

You can score it now with the evaluator:

```bash
agent-eval score --input your-use-case.yaml
```

## 7. Triage decision

- **Decision:** ☐ Proceed to risk assessment ☐ Redesign ☐ Reject
- **Decided by / date:**
- **Rationale:**
