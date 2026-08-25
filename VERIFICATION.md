# Verification log — regulatory_sources.yaml

`verification.owner_verified` is `false`. This file records what has been checked, by what
means, and what a person still has to do to change that flag. It exists so the gap between
"recorded and pinned" and "read back against the primary text" is a list with a length rather
than a feeling.

Read [what this maps, and what it does not](docs/00-scope/regulatory-scope.md) first — this log
is the evidence behind that document's verification-status section.

**Why this file sits outside `docs/`.** The reference checker requires that any document under
`docs/` citing article numbers be bound to exactly one framework, because a bare "Art. 9" means
different things in different acts. That rule is right and this document cannot satisfy it: a
correction list has to name articles, and it spans both acts. Every reference below therefore
names its act explicitly, which is the guarantee the rule exists to provide.

## Pass of 2026-08-25 — assisted review, not primary source

**Method.** Every reference in `regulatory_sources.yaml` was checked article by article against
the consolidated texts. **EUR-Lex could not be reached directly:** it answers automated requests
with HTTP 202 and an empty body, so part of the check fell back on secondary renderings of the
official text. That is a cross-check, not verification.

**This pass therefore does not justify setting `owner_verified` to `true`.** What it does is
reduce the remaining work to the specific entries below.

**Confirmed.** CELEX identifiers, Official Journal citations and the consolidated version are
correct: `32024R1689`, `OJ L, 2024/1689, 12.7.2024`, consolidated `02024R1689-20260727`, the
amending act `32026R1744`, and `32022R2554` with `OJ L 333, 27.12.2022, pp. 1–79`. No newer
consolidated version of either act was found. The verification gap is entirely in the `topic`
labels — the descriptions — and not in the provenance.

### Correction required before the flag moves

| Ref | Recorded topic | Official heading (to confirm) |
|---|---|---|
| AI Act Art. 13 | `instructions for use (high-risk)` | *Transparency and provision of information to deployers* |

Article 13 is not about instructions for use; that is one obligation inside it. Every statement
derived from this reference inherits the mistake, which makes it a substantive error rather than
a wording preference.

### Corrections recommended in the same pass

| Ref | Recorded topic | Finding |
|---|---|---|
| DORA Art. 5–6 | `ICT risk management framework` | Art. 5 is *Governance and organisation*; only Art. 6 carries the recorded title. Split, or widen the label. |
| DORA Art. 28 | `ICT third-party risk` | The article heading is *General principles*; the recorded label is the section it sits under. This is also the one divergence the sister repository's cross-register test records. |
| DORA Art. 18 | `classification of ICT-related incidents` | Heading continues *…and cyber threats*. |
| DORA Art. 19 | `reporting of major ICT-related incidents` | Heading continues *…and voluntary notification of significant cyber threats* — a whole obligation is missing from the label. |
| AI Act Art. 51–55 | `general-purpose AI model obligations` | Art. 52 is *Procedure* and Art. 54 is *Authorised representatives*; neither is an obligation on providers. Widen the range label or split it. |
| AI Act Art. 10 | `data governance (high-risk)` | Heading is *Data and data governance*. Minor, and worth recording. |

### What closing this looks like

Open each reference in a browser, read the heading in the consolidated text, correct the six
entries above, run `agent-eval render-docs`, then set `owner_verified: true` and record the date
and method in the `verification` block. It is an hour of unglamorous work and it is the cheapest
credibility in this repository — every downstream artifact, including any tool that answers with
a citation, inherits whatever this flag says.

## Open questions

- The 2026-08-25 pass could not reach EUR-Lex directly. If that turns out to be a persistent
  block rather than a transient one, the honest options are a manual pass or an offline copy of
  the consolidated texts checked into the repository — not a scripted check that quietly reads
  something other than the source it names.
- The two acts are covered. ISO/IEC 42001, NIST AI RMF and MaRisk carry no references in this
  register at all, by the decision recorded in `BIBLE.md` INV-3; nothing here changes that.
