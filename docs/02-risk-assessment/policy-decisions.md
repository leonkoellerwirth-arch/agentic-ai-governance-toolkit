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
7 thresholds carry a judgement; 7 decisions are recorded.

| Threshold | Decision |
|---|---|
| `rubric.yaml#dimensions` | PD-DIMENSIONS-001 |
| `rubric.yaml#scale` | PD-SCALE-001 |
| `rubric.yaml#aggregation.method` | PD-AGG-001 |
| `rubric.yaml#aggregation.bands` | PD-BANDS-001 |
| `rubric.yaml#aggregation.overrides.action_space` | PD-OVERRIDE-ACTION-SPACE |
| `rubric.yaml#aggregation.overrides.reversibility` | PD-OVERRIDE-REVERSIBILITY |
| `rubric.yaml#aggregation.overrides.data_sensitivity` | PD-OVERRIDE-DATA-SENSITIVITY |
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
