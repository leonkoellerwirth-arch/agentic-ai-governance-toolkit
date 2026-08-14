# HANDOFF — agentic-ai-governance-toolkit

Session handoffs, **newest entry first**. Written by `/session-stop` (via
`scripts/session-snapshot.sh`). Read the top entry at `/session-start`.

## 2026-08-14 — Session 4 (source lock, sector-independent gaps, decision register)

_HEAD main · gate PASS · 21 files · INV-5 and INV-6 added_

- **Done:** Held the external concept review against the recorded decisions, then executed the three
  steps it produced — all of them repairs to what is **already published**, before anything new is
  built.
  - **INV-5, regulatory source lock.** `evaluator/src/agent_evaluator/regulatory_sources.yaml` pins
    every article the checklists cite to an act, CELEX id, Official Journal citation, and the
    consolidated version it was checked against, with the EUR-Lex URLs of that check. The 44
    references were published with "verify" markers but **no version anchor**, and the AI Act was
    amended by Regulation (EU) 2026/1744 (in force 2026-07-27) after they were written. Source-lock
    headers render into all four checklists (DE + EN) and into
    `docs/03-checklists/regulatory-sources.md`. The check runs both ways and also fails if any
    document under `docs/` cites an article without being bound to a framework.
  - **Sector-independent gaps closed.** `docs/05-monitoring/incident-response.md` and
    `docs/04-operating-model/provider-dependency.md` — both previously existed only inside the DORA
    checklist, which binds defined financial entities. The EU AI Act checklist gained the incident
    section it was missing (DE + EN).
  - **INV-6, policy-decision register.** `policy_decisions.yaml` records every threshold that is a
    judgement rather than a derivation, with its reasoning, external support where any exists, and
    **what it accepts as a cost**. The thresholds needing cover are computed from `rubric.yaml`, so
    a new band or override cannot land without its decision.
  - **`DEMO-` prefixes** in every logging example, plus the convention stated where the example
    lives. It was three fields, not one, and a second location nobody had listed
    (`evaluator/examples/logs-sample.jsonl`).
- **Decided:** (register entries in `BIBLE.md`) — Article references live **only in the checklists**;
  prose points at checklist rows. The source lock carries **provenance only**: never deadlines,
  penalties, or what an obligation requires, because recording which text applies is not legal
  advice and stating what it demands would be. Regulatory facts are never taken from commentary or
  from an AI review — only from EUR-Lex. Band boundaries 10/16/22 are named in the register as the
  least defensible number in the rubric. Minimum aggregation is a deliberate non-compensatory rule,
  **not** "methodically correct". Entitlements/IAM stays a declared simplification for v1 — a
  seventh dimension would demand more than the toolkit demands, the same principle that keeps
  `assurance` at R1 for C2.
- **Open:** Two owner decisions, both strategy rather than method: where the **practitioner evidence
  layer** lives (talks, interviews, market observation), and **which channels and people** to
  approach. Also `verification.owner_verified: false` in the source lock — a human still has to open
  the four EUR-Lex links and confirm the entries by eye.
- **Next:** S·01 — bring the readiness rubric into the source tree with a loader, a consistency
  test, and `agent-eval readiness`. It cannot land without its own policy decisions (minimum rule,
  required level per control level, PD-ASSURANCE-001); the INV-6 check demands them the moment the
  file exists. Independent of all building: the two or three targeted approaches in the existing
  network, which need nothing that does not already exist and have been open since the concept was
  written.
- **Continuity warnings:**
  - `local/` is **git-ignored**. The concept, the review, and the adjudication
    (`local/05-methodologie.md`, which is the authority for the corrected build order) exist only on
    this machine. This HANDOFF entry is the repo-side record.
  - The readiness draft `local/03-readiness-entwurf.yaml` **had never parsed** — an unquoted colon in
    an anchor. Fixed. S·01 should begin with loader and test, not with polishing anchors.
  - Sessions 2 and 3 left no HANDOFF entry; the entry below is reconstructed from git and from the
    working notes.

## 2026-07-23 / 2026-08-13 — Sessions 2 and 3 (reconstructed from git)

_No entry was written at the time; recorded here so the gap is visible rather than silent._

- **Done:** Merged the governance console (PR #11) to main. Corrected the author links and the
  LinkedIn slug across four repos; made `leon-koellerwirth.com` canonical everywhere. Replaced the
  `LICENSE` files so GitHub detects MIT (dual licence moved to `LICENSE-docs`). Sharpened the
  console disclaimer to name it a review tool, not a certification. Cleared advisories that had
  appeared since the last green run (`fast-uri`, and five more).
- **Continuity warnings:** These sessions are documented only by their commits and by the working
  notes in `local/`.

## 2026-07-13 — Session 1 (build v0.1.0)

_HEAD main · gate PASS · CI green · released v0.1.0_

- **Done:** Built the whole toolkit M1–M7 per the briefing. Replaced the GPL-3.0 LICENSE with a
  dual license (MIT code + CC BY 4.0 docs). Risk model with a single-source `rubric.yaml` (docs
  rendered from it, consistency-tested); seven-phase lifecycle + Mermaid; EU AI Act & DORA
  checklists (EN/DE) + go-live gate; operating model + monitoring + templates; evaluator complete
  (`score`, `policy-check`, `log-analyze`, optional `judge`). Tagged and released **v0.1.0** with a
  signed wheel/sdist + SBOM. Removed Dependabot per owner preference.
- **Decided:** Python project lives under `evaluator/`; `gate.sh`, `ci.yml`, and `release.yml`
  tailored to it. Diagrams ship as embedded Mermaid (+ `.mmd` sources), no pre-rendered SVGs.
- **Open:** Optional future work — pre-rendered SVGs, more worked examples, calibrated rubric weights.
- **Next:** Announce/link the repo (author task). Address any issues/feedback.
- **Continuity warnings:** The briefing file is intentionally git-ignored (the gate forbids tracking
  it). Never commit customer names; all examples are the fictional "Nordbank".

## 2026-07-13 — Session 0 (scaffold)

_HEAD — · commits-ahead — · gate PASS · secure: pending first push_

- **Done:** Repo scaffolded from `base` (existing repo template).
- **Decided:** Adopt the paved road — backbone gate, session skills, canonical agent config.
- **Open:** Fill in the first real feature scope in `BIBLE.md`.
- **Next:** `./setup.sh` (or `npm ci`), run `./scripts/gate.sh`, first commit + push.
- **Continuity warnings:** none yet.
