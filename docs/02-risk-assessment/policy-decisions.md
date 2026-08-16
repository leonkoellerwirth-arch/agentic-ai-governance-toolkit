# Policy decisions — which numbers are judgement, and whose

The README says the rubric is *a starting point, not a calibrated standard, and the thresholds are
illustrative*. That is honest, and it is useless to someone who has to defend a control level in a
review. This page is the long version.

Every threshold in the rubric is one of two things:

- **Derived** — traceable to a demand the toolkit already makes somewhere else. Recorded in the
  rubric itself, next to the thing it justifies.
- **A policy decision** — a judgement call. Recorded here, with the reasoning, the support (if any)
  from outside this project, and **what the decision gets wrong on purpose**.

Nothing may be neither. The list of thresholds needing cover is computed from
[`rubric.yaml`](../../evaluator/src/agent_evaluator/rubric.yaml) itself, so adding a band or an
override without recording the decision fails the check — and a decision pointing at a threshold
that no longer exists fails it too.

> **What this page is for.** The first serious question after any presentation of a scoring model is
> *"what is the data behind your thresholds?"*. For this rubric the answer is: reasoned practitioner
> judgement, no outcome data. A model that says so in writing, and names what each choice costs, is
> more useful than one that implies a calibration it does not have.

## Coverage

<!-- GENERATED:policy_coverage START — edit policy_decisions.yaml, then run `agent-eval render-docs` -->
17 thresholds carry a judgement; 17 decisions are recorded.

| Threshold | Decision |
|---|---|
| `rubric.yaml#dimensions` | PD-DIMENSIONS-001 |
| `rubric.yaml#scale` | PD-SCALE-001 |
| `rubric.yaml#aggregation.method` | PD-AGG-001 |
| `rubric.yaml#aggregation.bands` | PD-BANDS-001 |
| `rubric.yaml#aggregation.overrides.action_space` | PD-OVERRIDE-ACTION-SPACE |
| `rubric.yaml#aggregation.overrides.reversibility` | PD-OVERRIDE-REVERSIBILITY |
| `rubric.yaml#aggregation.overrides.data_sensitivity` | PD-OVERRIDE-DATA-SENSITIVITY |
| `readiness.yaml#dimensions` | PD-R-DIMENSIONS-001 |
| `readiness.yaml#scale` | PD-R-SCALE-001 |
| `readiness.yaml#dimensions.inventory.required` | PD-R-REQ-INVENTORY |
| `readiness.yaml#dimensions.oversight.required` | PD-R-REQ-OVERSIGHT |
| `readiness.yaml#dimensions.traceability.required` | PD-R-REQ-TRACEABILITY |
| `readiness.yaml#dimensions.containment.required` | PD-R-REQ-CONTAINMENT |
| `readiness.yaml#dimensions.assurance.required` | PD-ASSURANCE-001 |
| `readiness.yaml#dimensions.currency.required` | PD-R-REQ-CURRENCY |
| `readiness.yaml#aggregation.per_dimension` | PD-R-AGG-001 |
| `readiness.yaml#aggregation.exposure` | PD-R-EXPOSURE-001 |
<!-- GENERATED:policy_coverage END -->

## The decisions

<!-- GENERATED:policy_decisions START — edit policy_decisions.yaml, then run `agent-eval render-docs` -->
### PD-DIMENSIONS-001 — Six dimensions, each scored 1–5 against observable anchors.

**Applies to** `rubric.yaml#dimensions` · **status** `project_policy`

**Why**

- Each dimension names something a reviewer can ask for evidence about and be told no. "How autonomous is it?" is answerable; "how mature are you?" is not.
- Five steps: three collapses everything interesting into the middle, seven invites a precision the anchors cannot carry.
- These six change what controls an agent needs. Cost, business value, and model quality do not, and are deliberately absent.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

The dimensions are not independent — an agent with a wide action space usually also scores high on blast radius. Summing them treats correlated risk as if it were additive, which counts some of it twice. The alternative (a weighted or conditional model) would need calibration data that does not exist.

### PD-SCALE-001 — The scale runs 1–5, with 1 as the lowest meaningful score — not 0.

**Applies to** `rubric.yaml#scale` · **status** `project_policy`

**Why**

- Every agent in production has some autonomy, some action space, and some blast radius. A zero would claim an absence that does not occur once an agent is running.
- The readiness rubric does the opposite and starts at R0, because "no control at all" is a real and common state. Exposure and readiness are not symmetric.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

The minimum total is 6, not 0, so the numbers do not read as a percentage. That is intentional, but it does mean the total cannot be shared without the bands.

### PD-AGG-001 — Sum the six dimensions with equal weight.

**Applies to** `rubric.yaml#aggregation.method` · **status** `project_policy`

**Why**

- Weights would have to come from somewhere. There is no outcome data behind this rubric, so any weighting would encode a preference while looking like a measurement.
- A sum can be recomputed by hand from the scored dimensions. Anyone in a review can check the arithmetic without the tool.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

Equal weight is itself a claim: it says explainability matters as much as blast radius. It does not. The override rules are the correction — they let a single categorical risk raise the floor without pretending the sum knew about it.

### PD-BANDS-001 — Band boundaries at 10 / 16 / 22 — C1 6–10, C2 11–16, C3 17–22, C4 23–30.

**Applies to** `rubric.yaml#aggregation.bands` · **status** `project_policy`

**Why**

- The cuts are placed so that an assistive agent scoring low across the board lands in C1, an agent writing to a system of record under human approval lands in C2–C3, and an agent that is high on several dimensions at once lands in C4.
- C2 is deliberately the widest band. It is the band whose controls a normal organization can actually staff, and most production agents belong there.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

THIS IS THE LEAST DEFENSIBLE NUMBER IN THE RUBRIC, and it should be said first rather than discovered. The boundaries are not calibrated against incident data, because none was available. An agent scoring 16 and one scoring 17 differ by one point and by an entire control regime, and nothing empirical distinguishes them. Anyone applying this in anger should expect to move the cuts against their own incident history — and should record it when they do, which is what this file is for.

### PD-OVERRIDE-ACTION-SPACE — An action space of 5 forces a floor of C4, whatever the total.

**Applies to** `rubric.yaml#aggregation.overrides.action_space` · **status** `project_policy`

**Why**

- Acting on the outside world — moving funds, sending an external message, forming an obligation — is categorical, not additive. A low total does not make an irreversible external act light-touch.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

An otherwise trivial agent that can send one external message is governed like a payments agent. Deliberate: the failure mode is the message, not the volume. The cost is a control regime that will feel disproportionate to the team running it, and that argument will be had repeatedly.

### PD-OVERRIDE-REVERSIBILITY — Reversibility of 5 forces a floor of C3.

**Applies to** `rubric.yaml#aggregation.overrides.reversibility` · **status** `project_policy`

**Why**

- What cannot be undone must be stopped before it happens; that is a human in the loop, which is where C3 starts.
- C3 rather than C4 because irreversibility alone, without reach, affects one case at a time. Reach is what blast radius scores.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

An irreversible action with wide reach reaches C4 only via the total or the action-space override. If both are low and the effect is still catastrophic, the rubric under-rates it.

### PD-OVERRIDE-DATA-SENSITIVITY — Data sensitivity of 5 forces a floor of C3.

**Applies to** `rubric.yaml#aggregation.overrides.data_sensitivity` · **status** `project_policy`

**Why**

- Special-category personal data and secrets carry duties that do not scale down with how few records are touched.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

Overrides only ever raise the floor, never lower it. An agent touching one credential in a strictly bounded way gets C3 controls it may not need. That is the cheaper error of the two, and the exception path exists for the rest.

### PD-R-DIMENSIONS-001 — Six readiness dimensions, each derived from a demand the toolkit already makes.

**Applies to** `readiness.yaml#dimensions` · **status** `project_policy`

**Why**

- Every dimension points at an existing artefact — the C1–C4 control lists, the go-live gate, the logging requirements, the KPI catalog, decision rights, RACI. `derived_from` records which, so the claim "nothing here is invented" is checkable rather than asserted.
- Each dimension names something a reviewer can ask for evidence about and be told no. The `probe` field is that question in its shortest form: a dimension that cannot be probed would be a maturity opinion, not a readiness measurement.
- Six, and not more, because a dimension without a demand behind it would have to be invented. Identity and access management is the clearest candidate for a seventh and is recorded as a known simplification instead — see `simplifications.entitlements`.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

The dimensions inherit whatever the toolkit's own control lists get wrong. If a control is missing there, readiness cannot see it — the rubric measures conformance to this toolkit, not to the state of the art. Entitlements is the known instance: an agent can be confined to its documented action space and still hold credentials reaching systems that never appear in it, and this rubric will score that organization as ready.

### PD-R-SCALE-001 — The readiness scale runs R0–R3, and R0 is honestly zero.

**Applies to** `readiness.yaml#scale` · **status** `project_policy`

**Why**

- Exposure starts at 1 because every running agent has some autonomy. Readiness starts at 0 because "no decision trail at all" and "no defined stop at all" are real, common states, and a scale that cannot express them flatters every organization that is in one.
- Four steps, not five: the anchors distinguish absent, described, demonstrated, and sustained. A fifth step would need a distinction the evidence behind it cannot carry.
- The R2 anchors are deliberately written as demonstrations rather than as existence claims — "has been triggered at least once", "the refusal path is covered by a test". That is what makes R2 the meaningful threshold and R1 the honest resting place for paper controls.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

Four steps compress the distance between a mature organization and an exceptional one: R3 has to cover everything from "reconciliation happens" to "reconciliation finds discrepancies". An organization at a genuine R3 gets no room above it, so the rubric cannot show improvement past the point where it stops being interesting to a reviewer.

### PD-R-REQ-INVENTORY — Inventory clarity required at R1/R2/R2/R3 for C1/C2/C3/C4.

**Applies to** `readiness.yaml#dimensions.inventory.required` · **status** `project_policy`

**Why**

- Derived: the C1 control list demands only a recorded owner (R1). C2 adds documented intake and a risk assessment on file, which is the R2 anchor, and C3 adds nothing further to the registry itself — so C3 stays at R2 rather than inventing a demand.
- C4 reaches R3 because the value-chain role and the provider and model dependencies are what the go-live gate and the provider-dependency doc require at that level; periodic reconciliation is the only way those stay true rather than being true once.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

C3 and C2 carry the same requirement, so the rubric cannot distinguish an organization that merely registered its C3 agents from one that governs them well. Inventory is the dimension where a self-assessment is cheapest to pass and where passing means least.

### PD-R-REQ-OVERSIGHT — Action space and intervention required at R1/R2/R2/R3 for C1/C2/C3/C4.

**Applies to** `readiness.yaml#dimensions.oversight.required` · **status** `project_policy`

**Why**

- Derived: technical enforcement of the action space plus a tested refusal path is the R2 anchor, and it is what the C2 control list already implies once an agent writes anywhere. The explicit human gate that C3 demands is inside the same anchor, so C3 stays at R2.
- C4 reaches R3 because per-action pre-authorization is a C4 control verbatim, and because the blocked-action rate only means something if it is watched rather than merely written down.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

A C3 agent and a C2 agent are held to the same enforcement standard, which understates how much more a human-in-the-loop gate costs to run than a documented boundary. The rubric sees that the gate exists; it does not see whether the humans behind it have the time to use it, and a rubber-stamped approval scores exactly like a considered one.

### PD-R-REQ-TRACEABILITY — Reconstructability required at R1/R2/R3/R3 for C1/C2/C3/C4 — the only dimension at R3 by C3.

**Applies to** `readiness.yaml#dimensions.traceability.required` · **status** `project_policy`

**Why**

- Derived: the mandatory log fields are an R2 anchor and apply from C2. C3 reaches R3 because an audit trail an agent could rewrite is not an audit trail, and integrity protection is the difference between the R2 and R3 anchors.
- This is the only dimension pulled to R3 one level early. The reason is asymmetry of repair: every other gap can be closed going forward, but a decision that was never traceable cannot be made traceable afterwards. The evidence is either there at the time or it is gone.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

C3 organizations are held to a standard the C3 control list does not literally spell out — the one place this rubric demands slightly more than the exposure rubric, justified by the irreversibility above and named here rather than hidden. The practical cost is real: retention rules, restricted read access, and append-only storage are the most expensive R3 in the set, and an organization can reasonably decide the trade is not worth it for its C3 agents.

### PD-R-REQ-CONTAINMENT — Stop and roll back required at R0/R1/R2/R3 — the only dimension whose requirement starts at zero.

**Applies to** `readiness.yaml#dimensions.containment.required` · **status** `project_policy`

**Why**

- Derived: the C1 control list demands no kill-switch, so demanding one would ask more than the exposure rubric does. A read-only assistant is stopped by turning it off, and pretending otherwise would make the whole scale unfalsifiable at the bottom.
- R2 requires that the kill-switch has actually been triggered under realistic conditions with a measured time to effect. A documented but never-exercised stop path is R1 by construction — that distinction is the point of the dimension.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

A C1 agent with no stop path at all is scored ready on this dimension. That is defensible only as long as the control level is right; a mis-scored C1 agent that in fact writes somewhere inherits a blind spot here rather than a gap, and this rubric cannot detect the mis-scoring because it takes the control level as given.

### PD-ASSURANCE-001 — Independent assurance required at R1/R1/R2/R3 — C2 stays at R1, deliberately.

**Applies to** `readiness.yaml#dimensions.assurance.required` · **status** `project_policy`

**Why**

- Derived, and the derivation is the whole argument: the C2 control list demands a named, signing owner and nothing more. Independent 2nd-line review first appears as a C3 control. Requiring R2 at C2 would make the readiness rubric demand more than the exposure rubric, which is exactly the failure mode `derived_from` exists to prevent.
- Keeping the two rubrics consistent is worth more than tightening one number. If C2 should demand independent review, the correction belongs in the C2 control list in `rubric.yaml`, where it would apply to everything downstream — not smuggled in here.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

Stated rather than hidden: a C2 agent writing into systems the business depends on may be signed off by the team that built it. That is a real exposure, and this rubric will not flag it. Anyone who finds the trade unacceptable should raise the C2 control list rather than this row, and should expect the readiness bar to follow automatically.

### PD-R-REQ-CURRENCY — Currency required at R1/R2/R2/R3 for C1/C2/C3/C4.

**Applies to** `readiness.yaml#dimensions.currency.required` · **status** `project_policy`

**Why**

- Derived: C1 re-assesses on material change (R1); C2 adds monitored operational KPIs and an annual re-assessment, which is the R2 anchor. C3 keeps R2 — the quarterly cadence it adds is a frequency, not a new capability.
- C4 reaches R3 because R3 is the only anchor that asks whether the cadence is actually being met and whether a breached threshold has ever been escalated in practice.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

The rubric measures that re-assessment happens, never whether it finds anything. An organization that re-assesses quarterly and changes nothing scores identically to one whose re-assessments produce findings — the more valuable of the two is invisible here.

### PD-R-AGG-001 — Non-compensatory minimum: required is the highest any agent triggers, achieved is the lowest reached by an agent that triggers it. No single index value is produced.

**Applies to** `readiness.yaml#aggregation.per_dimension` · **status** `project_policy`

**Why**

- This is a chosen decision rule, not a proven correctness. It is stated that way on purpose: a weak critical control should not be compensated by strong values elsewhere, because the organization is reached through its weakest high-risk agent, not through its average one.
- A mean would be flattered by harmless agents. An organization with nine C1 assistants and one C4 payments agent would average its way to a comfortable number while the only agent that can cause real damage sits unguarded.
- No 0–100 index, because a single number invites optimizing the number instead of the control. "4 of 6 at exposure C3" cannot be quoted without its exposure, which is the property that makes it safe to share.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

A minimum is brittle and easy to argue with: one agent at R1 drags the dimension to R1 no matter how good the other twenty are, and the organization will experience that as unfair. The per-dimension detail ("1 of 3 C4 agents below target") is the mitigation, not a fix — it separates a single site from a systemic gap without changing the headline. Refusing a single score also costs real adoption: an index is what a management report asks for, and this rubric will lose to one that offers a number.

### PD-R-EXPOSURE-001 — Organizational exposure is the highest control level in production, not a distribution.

**Applies to** `readiness.yaml#aggregation.exposure` · **status** `project_policy`

**Why**

- Readiness has to be measured against something. The alternative — measuring against the typical agent — would let an organization running one C4 payments agent report itself against C2, which is the exact self-deception this rubric exists to prevent.
- The choice is stated in the rubric as a `known_bias` rather than defended as neutral. A risk function reads it as correct; a delivery function reads it as unfair. Both readings are available to anyone who sees the result, because the result always carries its exposure.

**Support outside this project**

- None. This is a judgement call, and is recorded as one.

**What it accepts as a cost**

One agent sets the bar for the entire organization, so the readiness figure says nothing about how far the other agents are from it and can shift a whole control level when a single agent is retired. An organization can also lower its exposure by decommissioning one agent rather than by improving anything — the rubric would record that as progress, and in a narrow sense it is.
<!-- GENERATED:policy_decisions END -->

## If you adopt this rubric

Change the numbers — that is what they are for. But change them **here**, in the register, and not
only in the YAML:

1. Move the threshold in `rubric.yaml`.
2. Update or supersede the decision in `policy_decisions.yaml`: what you changed, why, and what your
   version now accepts as a cost.
3. Run `agent-eval render-docs`.

A threshold moved without a recorded reason is indistinguishable, six months later, from a threshold
that was never thought about. That is the failure this register exists to prevent — and it is the
one that shows up in an audit, not in a test.
