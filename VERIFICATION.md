# Verification log — regulatory_sources.yaml

`verification.owner_verified` is `true` since 2026-08-25. This file records what has been checked, by what
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

## Pass of 2026-08-25 — against the primary text

**Method.** Every article heading in `regulatory_sources.yaml` was compared against the primary
text, retrieved from the **Publications Office Cellar repository**:

```
http://publications.europa.eu/resource/celex/{CELEX}
Accept: application/xhtml+xml
Accept-Language: eng
```

That is the official machine interface to the same text EUR-Lex renders. It matters that it is not
EUR-Lex itself: the EUR-Lex web pages answer automated requests with HTTP 202 and an empty body, so
anything scraping them reads a challenge page rather than the law. An earlier pass on the same day
hit exactly that wall, fell back on secondary renderings, and correctly declined to call itself
verification.

**Repeatable, not recounted.** The headings are committed as
[`official_headings.json`](evaluator/src/agent_evaluator/official_headings.json), refreshed by
[`scripts/refresh-official-headings.sh`](scripts/refresh-official-headings.sh), and four tests
compare the register against them on every run. A topic that starts claiming something the heading
does not carry fails the build. Re-running the refresh against the live source reproduces the
committed file byte for byte.

**Confirmed.** CELEX identifiers, Official Journal citations, the consolidated version
`02024R1689-20260727` and the amending act `32026R1744` are correct, as are `32022R2554` and its
citation. No newer consolidated version exists for either act.

### Seven topics corrected

| Ref | Was | Primary text says | Why it mattered |
|---|---|---|---|
| AI Act Art. 13 | `instructions for use` | *Transparency and provision of information to deployers* | **The substantive one.** Instructions for use are one obligation inside an article about transparency. Every statement derived from the reference inherited the mistake. |
| AI Act Art. 10 | `data governance` | *Data and data governance* | The article covers the data as well as its governance. |
| AI Act Art. 51–55 | `general-purpose AI model obligations` | Art. 52 is *Procedure*, Art. 54 *Authorised representatives* | Neither is an obligation on providers; the range label was narrower than the range. |
| DORA Art. 5–6 | `ICT risk management framework` | Art. 5 is *Governance and organisation* | Only Art. 6 carried the recorded title. |
| DORA Art. 18 | `classification of ICT-related incidents` | *…and cyber threats* | Half the heading was missing. |
| DORA Art. 19 | `reporting of major ICT-related incidents` | *…and voluntary notification of significant cyber threats* | A whole obligation was missing from the label. |
| DORA Art. 28 | `ICT third-party risk` | *General principles* | The article sits in the chapter *Managing of ICT third-party risk*; the label described the chapter and pointed away from the article. |

### Four context additions, declared

Four topics carry a word the heading does not, and each is declared in the snapshot with a reason:
Annex III and Annex IV have headings that are cross-references rather than descriptions; Art. 72
names the plan while the article establishes the system; and DORA Art. 28's heading is the bare
words *General principles*, which say nothing without the section they open. Anything undeclared
fails the build, so the exception list is where a wrong label would otherwise hide — and a test
fails if a declared exception is no longer needed.

### Four checklist rows inherited the same narrowing

Correcting a label does not correct what was written under it. Four rows had been drafted to the
old, narrower topic and were widened to the article they cite:

| Row | Was missing |
|---|---|
| AI Act 2.3 | The article requires the system be transparent enough for a deployer to interpret its output. The row asked only for instructions. |
| AI Act 1.4 | Classification of the model and, for a non-EU provider, the authorised representative — neither is an "obligation on providers", which is all the row asked for. |
| DORA 5.2 | Cyber threats. The row classified incidents only. |
| DORA 5.3 | The voluntary notification of a significant cyber threat, and who decides on it. |

This is the part of a label correction that is easy to skip: the register is the citation, the rows
are what someone actually works through, and a row narrower than its article quietly narrows the
review that uses it.

### What the flag now means

`owner_verified: true` here means: every cited heading was checked against the primary text from
the Publications Office, the check is committed and re-runnable, and the build fails if a label
drifts from it. It does not mean a lawyer has read the register, and it never did — whether an
obligation applies to a given system is [not something this project
answers](docs/00-scope/regulatory-scope.md).

## Open questions

- The snapshot covers the two acts this toolkit cites. ISO/IEC 42001, NIST AI RMF and MaRisk carry
  no references here at all, by the decision recorded in `BIBLE.md` INV-3.
- Cellar serves the consolidated text at the CELEX pinned in the register. When a newer
  consolidation appears, the pin has to move first — the refresh script follows the pin and will
  not notice on its own.
- The MaRisk 9th amendment (June 2026) is unassessed; it is outside this register.
