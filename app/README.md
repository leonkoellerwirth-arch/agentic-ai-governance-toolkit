# Governance Console (`app/`)

A local, offline-capable web console for the agentic-ai-governance-toolkit. It walks a user
through the six risk dimensions of the toolkit's scoring rubric and computes the C1–C4 control
band **in the browser**, mirroring the `agent-eval score` CLI.

> **A reference pattern, not a product.** This is a readable, adaptable work sample — not a
> deployable compliance tool and not legal advice. The rubric and scores are illustrative. See the
> repository `README.md` and `DISCLAIMER.md`.

## Design invariants

- **One rubric, one source (INV-1).** The console does not carry its own copy of the rubric. It
  reads `evaluator/src/agent_evaluator/rubric.yaml` at build time; the scoring logic mirrors
  `evaluator/src/agent_evaluator/risk_score.py`, guarded by tests. Never hardcode rubric data.
- **Everything runs (INV-4).** `npm run verify:ci` is the web analog of the repo's hard gate
  (`scripts/gate.sh` runs it automatically once `app/node_modules` is present). CI mirrors it.
- **No network.** The app makes no external calls; it is fully static and offline from first paint.

## Develop

```sh
cd app
npm ci
npm run dev        # http://localhost:5273
```

## Verify (the web gate)

```sh
npm run verify:ci  # typecheck · lint · tests · build
```

## Build

```sh
npm run build      # static output in app/dist/
npm run preview    # serve the built output locally
```

## Stack

Scaffolded from the `dev/base` paved road (`templates/vite-react-pwa`): Vite + React 19 +
TypeScript (strict) + Tailwind 4 + Vitest, with i18next (EN/DE). PWA is kept for offline use; the
template's SFTP deploy step is intentionally dropped — the console ships as a static `dist/`.
