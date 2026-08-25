# The evidence format

A gate run writes one file per check and a `manifest.json` beside them. The manifest is what makes
the directory archivable rather than merely produced: it names the tool and its version,
fingerprints the rulesets that decided the outcome, records the commit under test and the time, and
carries a SHA-256 of every file the run wrote.

The schema is published here: [`evidence-manifest.schema.json`](evidence-manifest.schema.json).
It is version `1.0.0`, and that version moves independently of the tool — a consumer targets the
format while `agent-eval` changes underneath it.

## Why the rulesets are hashed and not just named

A version number records what someone claimed was in force. A digest records what actually was.
The manifest carries both: `tool.version` for provenance, and a per-file digest plus one over all
rulesets for the rules themselves. Two runs with the same tool version and different digests used
different rules, and the manifest says so without anyone having to notice.

## What a digest proves, and what it does not

It proves the set has not been edited since it was written. That is all.

It does not show that a check was authorised, that the input was complete, that a rule was
appropriate, or that no event was left out. An evidence trail that is tamper-evident and wrong is
still wrong — it is merely detectably unchanged. Saying so in the file itself is deliberate: a
manifest read as proof of correctness would be worse than no manifest.

## Reading one

```bash
agent-eval manifest --evidence governance-evidence --commit "$(git rev-parse --short HEAD)"
```

The gate does this automatically at the end of every run; the command exists for the case where
evidence was produced some other way.

## Is this a standard?

No, and calling it one would be premature. It is a specified, versioned, machine-checkable format
with a conformance suite ([`test_evidence_schema.py`](../../evaluator/tests/test_evidence_schema.py)),
written by exactly one tool. What would make it a format rather than an output is a second
implementation — one that writes manifests this suite accepts, or reads them and does something
useful.

## Open questions

- The manifest describes the artifacts; it does not specify **them**. A consumer still has to know
  what a `readiness.json` means. Stable identifiers for findings, controls, severities and statuses
  are the next thing missing, and they are a bigger piece of work than the envelope was.
- A digest names a ruleset it does not include. Verifying a run a year later means having the
  ruleset that was in force, and nothing here archives it.
- Nothing signs the manifest. Tamper-evidence within a set is not the same as authenticity of its
  origin, and an optional signature over the manifest is the obvious next step.
