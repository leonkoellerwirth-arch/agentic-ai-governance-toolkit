# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **The reference architecture now draws its enforcement instead of labelling it.** A second review
  pass found the redraw still claiming guarantees the picture did not show: the delegation broker
  issued a token nobody verified, `SOR → WORK` bypassed any pre-authorisation entirely, the
  escalating retrieval path ran straight to the index rather than through the gate, and "no model
  output admitted" was written on a broker whose request the worker — which sees model output —
  composed.

  Every data and tool access now crosses one **enforcement point** that verifies the token, the
  action and its parameters before the effect. The capability the broker executes is bound there
  rather than composed by the runtime, and the broker checks again at the sink. The automatic
  deletion and notification paths carry their preconditions on the arrow — legal-hold checked,
  scope not widened by the agent, recipient from the record, no generated free text — instead of
  leaving them to the matrix.

  Two answers in the questions table were corrected rather than softened: the human-approval list
  was incomplete against the matrix, and the refusal on secrets had been narrowed to "into the
  model context" while the matrix refuses the read outright.

### Added

- **Evidence manifest** ([`evidence.py`](evaluator/src/agent_evaluator/evidence.py), written by
  every gate run, also available as `agent-eval manifest --evidence <dir>`). The per-check JSON
  said what was found and nothing about where it came from — not which tool, not which rulesets,
  not when, not against which commit. An auditor opening that file a year later could not answer
  the first question they would be asked.

  The manifest answers it *beside* the results rather than inside them, so nothing consuming
  `agent-eval <command> --json` breaks: tool and version, a SHA-256 per ruleset file plus one over
  all of them, the commit under test, the timestamp, and a digest of every artifact the run wrote.

  **The rulesets are fingerprinted by content, not by version number.** A version number records
  what someone claimed; a digest records the rules that were actually in force. And the format
  carries its own `schema_version`, moved independently of the tool, because a consumer targets the
  format while the tool moves underneath it.

  The manifest states what it does not prove, in the file: digests show the set has not been edited
  since it was written. They show nothing about whether a check was authorised, complete or
  correct.

- **A published schema for that manifest**
  ([`docs/08-evidence/`](docs/08-evidence/)), with a conformance suite that validates the schema
  itself, every manifest the tool writes, and seven malformed shapes a second implementation would
  plausibly emit. A published schema nobody checks is documentation.

  The accompanying note declines the word *standard*. This is a specified, versioned,
  machine-checkable format written by exactly one tool; what would make it more than that is a
  second implementation. The open questions name what is still missing — stable identifiers for
  findings and controls, archiving the rulesets a digest points at, and signing the manifest.

- **`PD-AUTHORITY-001` now records the framework that disagrees with it.** SAFR — Safeguards for
  Agentic Finance at Runtime, convened by the Monetary Authority of Singapore with HSBC,
  J.P. Morgan, Mastercard, Visa and OCBC in July 2026 — resolves every proposed agent action to
  one of **four** dispositions: deny, escalate, auto-execute, or *observe*. This toolkit decided on
  three and wrote down why. The most serious published work on the same question came to a
  different answer.

  It is recorded in `external_support` as opposition rather than omitted, which is the only
  honest place for it. The cost it exposes is named: "observe" is not a weaker approval but an
  action that proceeds *and is looked at afterwards*, and this matrix cannot express that — it
  names an evidence artifact per row and never says whether anyone reads it, so "automatic"
  silently covers both "nobody looks" and "reviewed daily", a distinction the control levels
  themselves do make.

  The decision stands, on a discipline argument rather than a modelling one, and the entry states
  what would change it.

### Added

- **Consolidation check** ([`scripts/check-consolidations.sh`](scripts/check-consolidations.sh)):
  asks the Publications Office SPARQL endpoint which consolidated versions of a pinned act exist,
  and reports one newer than the pin as a finding. A pin is what makes a citation checkable and
  also what lets a register go quietly stale, because a pin never notices that the law moved.

  It found something on its first run: **DORA pinned the base act while a consolidation existed**,
  so the register could not have told whether the text had been amended. DORA is now pinned to
  `02022R2554-20221227` — a consolidation that carries no amendments, which is precisely the point:
  before, nothing here could establish that.

  The mechanism knows nothing about financial supervision. It takes a CELEX identifier and asks
  what consolidations exist, which works for the GDPR, NIS2, MiCA, the Data Act, the Cyber
  Resilience Act, the DSA and the Machinery Regulation alike — the last of which has three
  consolidations, the newest dated 27 July 2026, because the same Digital Omnibus that moved the AI
  Act's application dates amended it too.

  `consolidations.json` records what the endpoint answered and when, and three offline tests compare
  the register against it: every framework must pin a consolidation rather than a base act, the pin
  must be the newest recorded, and the snapshot must say when it was checked — because "no newer
  version" without a date is a claim with no shelf life.

### Fixed

- **Four checklist rows were widened to the articles they cite.** Correcting a label does not
  correct what was written under it: rows drafted to the old, narrower topics had inherited the
  same narrowing. The AI Act row on Article 13 asked only for instructions where the article
  requires the system be transparent enough for a deployer to interpret its output; the row on
  Articles 51–55 asked for provider obligations and not for the model's classification or, for a
  non-EU provider, the authorised representative. DORA's row 5.2 classified incidents but not
  cyber threats, and 5.3 knew the reporting paths but not who decides on a voluntary notification
  of a significant cyber threat. Both languages.

- **`owner_verified` is true, and it means something checkable.** Every cited article heading was
  compared against the primary text — not against a rendering of it — retrieved from the
  **Publications Office Cellar repository** with `Accept: application/xhtml+xml` and
  `Accept-Language: eng`. That detour matters: the EUR-Lex web pages answer automated requests with
  HTTP 202 and an empty body, so an earlier pass the same day had to fall back on secondary
  renderings and correctly refused to call itself verification.

  **Seven topics were wrong and are corrected.** The substantive one: the AI Act's Article 13 was
  labelled "instructions for use", which is one obligation inside an article about transparency and
  provision of information to deployers — every statement derived from that reference inherited the
  mistake. DORA's Article 28 described the chapter it sits in rather than the article. Articles 18
  and 19 each dropped half a heading, one of them a whole obligation. The full before-and-after is
  in `VERIFICATION.md`.

  **The check is committed, not recounted.** `official_headings.json` holds the headings,
  `scripts/refresh-official-headings.sh` re-derives them from the live source, and four tests fail
  the build if a topic starts claiming something the heading does not carry. Re-running the refresh
  reproduces the committed file byte for byte. Four topics legitimately add context — two annex
  headings are cross-references, Article 72 names the plan rather than the system, and DORA's
  Article 28 heading is the bare words "General principles" — and each is declared with a reason,
  with a further test that fails when a declared exception is no longer needed.

  One existing rule was widened rather than worked around: `test_provenance_of_the_provenance_is_recorded`
  required every source to be an EUR-Lex URL. Cellar is the same Publications Office repository
  EUR-Lex serves from and the only one a machine can read, so it is now accepted — and a new test
  refuses to let `owner_verified` stand without a source something could actually have read.


- **The checklists read as if deferred obligations were already in force.** Regulation (EU)
  2026/1744 — the Digital Omnibus on AI, in force since 27 July 2026 — moved the high-risk
  application dates to 2 December 2027 for standalone systems and 2 August 2028 for high-risk AI
  embedded in products already covered by Union product legislation. The transparency obligations
  and the AI-literacy duty were left where they were.

  The source lock already recorded the amending act, its CELEX id and its date of entry into
  force. It did not record what the act *did*, and a note in `regulatory_sources.yaml` saying so
  was never rendered. A practitioner opening the checklist in August 2026 therefore saw rows for
  risk management, technical documentation, record-keeping and post-market monitoring with nothing
  to indicate that none of them bind yet.

  The note is now concrete and rendered in both languages. This also narrows a rule in the source
  file: it still records no penalties and no statement about what an obligation requires of the
  reader, but an amending act's effect on application dates is provenance, not conclusion — it is
  part of which text is in force, and withholding it made the omission itself misleading.

### Added

- **[Reference architecture](docs/07-architecture/reference-architecture.md)** — one diagram for
  the questions an architect asks before opening any control catalogue, and a table underneath
  because a picture answers none of them precisely.

  The first draft failed its review on four counts and the corrections are the content. It had no
  **delegation broker**: "the requester's identity, carried through retrieval" is not a mechanism —
  retrieval can verify a scoped, time-bound token, it cannot establish one. It had no **tool and
  secret broker**, so a worker that both handles model output and holds credentials could be driven
  by prompt injection into a secret-using external call. Prompt and output hashes were drawn going
  to the *model* instead of to the trail. And four arrows asserted authorities the matrix regulates
  differently — retrieval as unconditional, every record change as gated, every external message as
  gated — which contradicted the automatic deletion, revocation and templated-notification paths.

  The document now also says what hashes are not: they bind content already known to whoever holds
  it, and prove neither that an access was authorised nor that no event was omitted. `scripts/render-diagrams.sh`
  walks every `docs/**/diagrams` directory instead of one hard-coded path.

- **[`OVERVIEW.md`](OVERVIEW.md)** — the entry document the portfolio did not have. Four
  repositories, one job, on one page: the problem, who has it, what you actually get, and what
  this deliberately is not.

  It also settles a positioning question that had been left open. This is a **decision support
  system, not a decision engine**: it structures the decision and produces the evidence for it,
  and does not make it. That is not modesty — a tool that answered "high-risk or not" would be
  promising exactly what `docs/00-scope/regulatory-scope.md` explains cannot be promised, and a
  reader who noticed the contradiction would be right to stop trusting the rest.

- **[What this does not build, and what does](docs/00-scope/what-this-does-not-build.md)** — the
  non-goals, with the products that cover them instead: agent identity and inventory (Microsoft
  Entra Agent ID / Agent 365), policy packs for the EU AI Act, NIST AI RMF, ISO 42001, SOC 2 and
  NYC Local Law 144 (Credo AI, resold by IBM), inline filtering (AWS, Google), fairness assessment
  (Holistic AI, Fairly AI), drift monitoring (IBM).

  The remaining gap is narrow and named: DORA, MaRisk and the GDPR at control level, with audit
  procedures in the language an internal-audit function writes in — plus a documented refusal and
  runtime enforcement short enough to read. Claims about other products are dated and sourced, and
  the file says which of them rests on public material rather than on certainty.

- **Action authority matrix**
  ([`action_authority.yaml`](evaluator/src/agent_evaluator/action_authority.yaml), rendered to
  [`docs/03-checklists/action-authority-matrix.md`](docs/03-checklists/action-authority-matrix.md)):
  24 actions in five groups, each automatic, gated on a competent person, or refused by design.
  The rubric says how much control an agent needs; this says what it is allowed to do.

  **Authority depends on the action's own context, never on the control band.** The first draft
  escalated at a band — "automatic below C3" — and an independent review took it apart: a band is
  the sum of six dimensions, so a system full of personal data can score C1 and C3 can arise with
  none in it at all. Authority now turns on purpose, data class, scope, recipient and whether a
  prior approval exists. The correction is recorded in `PD-AUTHORITY-CONDITIONS` rather than
  quietly applied. An automatic action with no stated precondition fails validation: blanket
  permission is the failure this file exists to make visible.

  **Decision and execution are separate rows.** The same review found the first draft forbidding
  the compliant path: executing a four-eyes-approved deletion rule is normal and sometimes
  required, automated revocation on a leaver event is good practice, and payment operations run on
  exactly the separation of preparation, approval and execution that a blanket refusal denies.
  Deciding ad hoc to delete stays refused; executing an approved rule does not. Choosing a payee
  stays refused; initiating an approved payment does not.

  **One criterion decides what is forbidden at all** — approval cannot repair it: the action
  destroys the evidence of itself, or moves the boundary from inside the boundary. Four rows meet
  it. Everything else, however severe, is approval with requirements, because a refusal teams
  route around is worse than a demanding approval they follow.

  **The judgements are registered under INV-6.** `required_targets()` now reads the matrix too, so
  a new authority model, a changed refusal criterion or a new conditional field without a recorded
  decision fails `render-docs --check` — the same invariant the rubrics already live under.
  Unregistered thresholds are personal preference wearing governance vocabulary.

  **The refusal criterion is checked, not stated.** A second review pass found the sharper
  version of the same problem: the criterion did not carry two of its own four refusals. Deciding
  to delete destroys nothing — execution does — and reading a secret neither destroys evidence nor
  moves a boundary. The criterion now has three named limbs (`evidence_destruction`,
  `boundary_move`, `instant_harm`), every refused row names the one it meets, and validation
  rejects a refusal whose limb is not declared. `decide-deletion` became
  `select-records-for-deletion` under approval, with the enforceable control being that the
  selector does not also execute and that the agent supplies no parameter widening an approved
  rule. The payment row lost a circular limb that refused any instance "without effective prior
  approval" while instance approval was the baseline.

  Five actions the first draft omitted are in: executing code, bulk export, deciding an individual
  case, changing production logic, and fetching external content. The document also reconciles
  itself with the scope statement rather than leaving the two side by side: this is a starting
  policy declared as judgement, not a finding derived from a legal text.

- **[`OVERVIEW.md`](OVERVIEW.md)** — the entry document the portfolio did not have. Four
  repositories, one job, on one page: the problem, who has it, what you actually get, and what
  this deliberately is not.

  It also settles a positioning question that had been left open. This is a **decision support
  system, not a decision engine**: it structures the decision and produces the evidence for it,
  and does not make it. That is not modesty — a tool that answered "high-risk or not" would be
  promising exactly what `docs/00-scope/regulatory-scope.md` explains cannot be promised, and a
  reader who noticed the contradiction would be right to stop trusting the rest.

- **[What this does not build, and what does](docs/00-scope/what-this-does-not-build.md)** — the
  non-goals, with the products that cover them instead: agent identity and inventory (Microsoft
  Entra Agent ID / Agent 365), policy packs for the EU AI Act, NIST AI RMF, ISO 42001, SOC 2 and
  NYC Local Law 144 (Credo AI, resold by IBM), inline filtering (AWS, Google), fairness assessment
  (Holistic AI, Fairly AI), drift monitoring (IBM).

  The remaining gap is narrow and named: DORA, MaRisk and the GDPR at control level, with audit
  procedures in the language an internal-audit function writes in — plus a documented refusal and
  runtime enforcement short enough to read. Claims about other products are dated and sourced, and
  the file says which of them rests on public material rather than on certainty.

- **Action authority matrix**
  ([`action_authority.yaml`](evaluator/src/agent_evaluator/action_authority.yaml), rendered to
  [`docs/03-checklists/action-authority-matrix.md`](docs/03-checklists/action-authority-matrix.md)):
  sixteen actions in five groups, each either automatic, gated on a named person, or refused by
  design. The rubric says how much control an agent needs; this says what it is allowed to do,
  which is the question a reviewer asks immediately afterwards and no rubric answers.

  **`escalates_at` is the load-bearing idea.** Few actions are categorically safe or categorically
  forbidden; most are safe until the blast radius grows. Reading personal data is automatic below
  C3 and gated from there up. The levels are checked against `rubric.yaml`, so an escalation to a
  band that does not exist fails the build rather than reading as a stricter rule than it is —
  the same cross-file invariant the readiness rubric already relies on.

  **Every row names an evidence artifact, including the forbidden ones.** A refusal that leaves no
  trace cannot be audited, and an attempt at a forbidden action is a finding in its own right.
  Validation also fails a matrix in which nothing is forbidden at all: one where everything passes
  given enough approval is not a boundary.

  Three rows are deliberately arguable and say so in the document — payments forbidden rather than
  escalated, deletion forbidden at every level, reading personal data escalating rather than being
  free or refused. A matrix adopted unchanged has not been thought about; the disagreements are
  the useful part.

  It enforces nothing, and the document leads with that. The enforcing half is a pre-action check
  in the runtime, for which `local-agent-pipeline` is the reference implementation.

- **Verification log** ([`VERIFICATION.md`](VERIFICATION.md)): what has been checked in
  `regulatory_sources.yaml`, by what means, and what a person still has to do before
  `owner_verified` can move. The gap between "recorded and pinned" and "read back against the
  primary text" is now a list with a length rather than a feeling.

  The 2026-08-25 pass confirms the provenance — CELEX identifiers, OJ citations, the consolidated
  version `02024R1689-20260727` and the amending act — and finds the gap to be entirely in the
  topic labels. One is wrong rather than imprecise: the AI Act's Article 13 is recorded as
  "instructions for use", which is one obligation inside an article about transparency and
  information to deployers. Five further labels omit half a heading or describe the section rather
  than the article. Each is listed with its proposed replacement.

  **The flag stays `false`.** EUR-Lex answers automated requests with an empty body, so the pass
  fell back in part on secondary renderings of the official text — a cross-check, not
  verification. Recording that limit is the point: a register whose value is citability cannot
  claim a confirmation it did not obtain. The remaining work is an hour with a browser, and the
  file says exactly which hour.

  The log sits at the repository root rather than under `docs/`, because the reference checker
  requires a citing document to be bound to one framework and a correction list spanning two acts
  cannot be. It names the act beside every article instead, which is the guarantee that rule
  exists to provide.

## [0.3.0] — 2026-08-25

### Changed

- **The gate no longer needs GitHub.** The logic moved out of `action.yml` into
  [`scripts/governance-gate.sh`](scripts/governance-gate.sh), which runs offline against nothing but
  the evaluator — a pre-commit hook, a Makefile target, GitLab, Jenkins, or by hand. It writes the
  same JSON evidence and a `summary.md` stamped with evaluator version, commit and UTC timestamp.
  `action.yml` is now a thin wrapper around it, so CI and the local run cannot drift
  (CONSTITUTION §4); the action adds the job summary and the evidence artifact, and nothing else.
  Exit codes are unchanged: 0 clean, 1 findings, 2 misconfiguration.

  This is the shape the gate should have had from the start. Reaching for a CI service first made
  the useful half of the tool depend on a budget that can run out.

## [0.2.1] — 2026-08-25

### Fixed

- **The gate ignored `fail-on-findings` and died on the first finding.** GitHub runs composite
  `run:` steps under `bash -e`; the script set `-uo pipefail` but never disabled errexit, so the
  first check that exited non-zero killed it before the flag was consulted — and before the
  remaining checks ran, so the evidence was incomplete too. `set +e` is now explicit, with the
  reason in a comment above it.

  Found by `governance-gate-selftest.yml` on the first run after release, which is the entire
  argument for asserting on the `passed` output rather than on job colour: the job it was
  supposedly testing had failed, and only the assertion said why. The local test harness now
  invokes the script the way the runner does (`bash --noprofile --norc -eo pipefail`), because
  a harness that is more forgiving than production tests nothing.

  `v0.2.0` carries the action but should not be pinned.

## [0.2.0] — 2026-08-25

### Added

- **Scope statement** ([`docs/00-scope/regulatory-scope.md`](docs/00-scope/regulatory-scope.md)):
  what this toolkit maps, what it deliberately does not, and why the three repositories answer that
  differently. Three questions that look alike — what an article requires (mapped), whether it
  applies to a given system (not mapped), how well an organization meets it (not scored) — with the
  reasoning for each boundary and where triage sits between the first two.

  This closes a gap that was visible from outside and not from inside: this toolkit maps the EU AI
  Act, `rag-approval-blueprint` declines to, and `platform-decision-kit` carries no regulatory
  checklist at all. Each position is sound on its own; read side by side and unexplained, they read
  as inconsistency. Linked from the README and `DISCLAIMER.md`. The document cites no article
  numbers of its own and points at the checklists instead, per the rule the reference checker
  already enforces on prose.

- **Governance gate as a composite action** (`action.yml`): the evaluator's exit codes were already
  a gate — `readiness`, `policy-check` and `log-analyze` each exit non-zero on a finding — but every
  consuming repository had to install the toolkit and know the CLI to use them. It now references
  the action instead, pinned to a tag, and the rubric travels with it rather than being copied.

  **The run is the evidence.** Each check writes machine-readable JSON to `governance-evidence/`,
  uploaded as a build artifact, and a readable block to the job summary — both stamped with the
  evaluator version, the commit under test and the run id. A reviewer reads the summary, an auditor
  reads the JSON, and neither depends on a screenshot. `fail-on-findings: "false"` reports without
  blocking, for a first rollout on a repository that has never been gated.

  Checks are opt-in per input and at least one is required; a misconfiguration (an `assessment`
  without a `policy`, or no check at all) exits 2 rather than degrading into a silent pass — as does
  an unreadable input file. `.github/workflows/governance-gate-selftest.yml` asserts all three
  directions on the action's `passed` output rather than on job colour, because a gate that never
  blocks is a green check that means nothing. The clean-input case is built in the runner and
  discarded with it; every committed example is a realistic negative case on purpose.

- **Agent readiness rubric** (INV-7): `evaluator/src/agent_evaluator/readiness.yaml` and the new
  `agent-eval readiness` command answer the half of the question the toolkit could not answer
  before. `rubric.yaml` scores what an agent can do to you; `readiness.yaml` scores whether the
  organization running it has the control that implies. Six dimensions (inventory, oversight,
  traceability, containment, assurance, currency), each scored R0–R3 against falsifiable anchors and
  each derived from a demand the toolkit already makes elsewhere. Rendered to
  [`docs/06-readiness/agent-readiness-rubric.md`](docs/06-readiness/agent-readiness-rubric.md);
  `evaluator/examples/org-readiness-demo.yaml` is a runnable fictional organization whose control
  levels are computed by `agent-eval score`, not asserted, so the two rubrics cannot drift apart.

  Readiness is measured **relative to the exposure actually in production**, never absolutely.
  Aggregation is a deliberately non-compensatory minimum — the requirement is the highest any agent
  triggers, the achieved level the lowest reached by an agent that triggers it — and **no 0–100
  index is produced**, because a single number invites optimizing the number instead of the control.
  Ten further entries in the policy-decision register cover every threshold the rubric introduces,
  including why `assurance` deliberately stays at R1 for C2 and why `traceability` is the one place
  readiness demands more than exposure does.
- **Regulatory source lock** (INV-5): `evaluator/src/agent_evaluator/regulatory_sources.yaml` pins
  every article the checklists cite to an act, a CELEX id, an Official Journal citation, and the
  consolidated version it was last checked against — with the EUR-Lex URLs of that check. Each
  checklist now carries a generated source-lock header, and
  [`docs/03-checklists/regulatory-sources.md`](docs/03-checklists/regulatory-sources.md) renders the
  full registry. `test_regulatory_sources.py` fails if a checklist cites an article the lock does
  not carry, or if the lock carries one no checklist cites. The lock records **which text applies**
  — never deadlines, penalties, or what an obligation requires.
- **Policy-decision register** (INV-6): `evaluator/src/agent_evaluator/policy_decisions.yaml` records
  every threshold that is a judgement call rather than a derivation — the reasoning, the external
  support where any exists, and **what the choice accepts as a cost**. Rendered to
  [`docs/02-risk-assessment/policy-decisions.md`](docs/02-risk-assessment/policy-decisions.md). The
  thresholds needing cover are computed from `rubric.yaml`, so a new band or override cannot land
  without its decision, and `test_policy_decisions.py` fails either way round.
- **Incident response** (docs/05): sector-independent handling for agent incidents — what counts as
  one, severity by control level, a five-step runbook, stop/rollback expectations per level, and the
  scenarios worth rehearsing. Previously this existed only in the DORA checklist, which binds
  defined financial entities.
- **Provider and model dependency** (docs/04): what to record per agent, concentration at the
  organization level, the three ways a provider changes underneath you, and exit expectations by
  control level. Also previously DORA-only.
- **Incident section in the EU AI Act checklist** (EN + DE): serious-incident definition and
  reporting paths, post-market monitoring feeding re-assessment, and provider-change triggers.

- Pre-rendered `.svg` versions of the three lifecycle diagrams, plus `scripts/render-diagrams.sh`
  to regenerate them from the `.mmd` sources.
- **Governance console** (`app/`): a static Vite/React surface for the risk assessment. It reads the
  same `rubric.yaml` as the evaluator (INV-1), walks the dimensions interactively, and shows the
  resulting risk class. Built and linted in the gate alongside the Python surface.

### Changed

- Every identifier in the logging examples now carries a `DEMO-` prefix, and the convention is
  stated where the example lives. A log line is the most copied artifact in a governance document;
  `"actor": "human:clerk-014"` read as a real personnel number and got reused as one.

## [0.1.0] — 2026-07-13

First public release.

### Added

- **Agent lifecycle** (docs/01): seven phases with goal, input/output, responsible role, and control
  point each, plus Mermaid diagrams (swimlane lifecycle, triage flow, escalation paths).
- **Risk model** (docs/02): six scoring dimensions (1–5) aggregating to control intensity C1–C4,
  with categorical overrides and minimum controls — defined once in `rubric.yaml` and rendered into
  the docs, with a consistency test. Three fictional worked examples.
- **Checklists** (docs/03): EU AI Act and DORA checklists for agents in English and German, plus a
  go-live readiness gate. Regulatory references are marked "verify" and carry a not-legal-advice note.
- **Operating model** (docs/04): roles & RACI, decision rights by control level, committee templates.
- **Monitoring** (docs/05): KPI catalog and audit-trail logging requirements.
- **Evaluator** (evaluator/): a Python CLI/library — `score`, `policy-check`, `log-analyze`, and an
  optional local LLM `judge` — with an offline test suite.
- **Templates**: use-case intake, agent registry entry, decommissioning protocol.
- Paved-road tooling: hard gate, CI across Python 3.11–3.13, security scanning, dual license
  (MIT for code, CC BY 4.0 for documentation).

[Unreleased]: https://github.com/leonkoellerwirth-arch/agentic-ai-governance-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/leonkoellerwirth-arch/agentic-ai-governance-toolkit/releases/tag/v0.1.0
