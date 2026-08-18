# Implementation status

The attached implementation specification is the architectural contract. It explicitly requires phase-by-phase delivery and designates the reminder workflow as the first vertical slice.

## Delivered in this commit

- Phase 0 foundation: monorepo layout, FastAPI, Next.js, Postgres/Redis Compose, typed configuration, database schema, CI, and health endpoint.
- Phase 1 kernel boundary: typed routing decision, run persistence, event stream, audit trail, bounded run budget record, policy boundary, dynamic route selection, and provider-neutral model interface.
- First Phase 2 vertical slice: deterministic reminder intent, timezone conversion, idempotency, durable persistence, postcondition read verification, user-legible SSE activity, and reminder UI confirmation.
- xAI integration boundary: `packages/models/xai_provider.py` owns the Responses API call; no harness imports a provider SDK or provider-specific response type.

## Desktop control plane

- `apps/desktop` is a Tauri 2 Windows app, using the system WebView rather than an Electron-bundled Chromium runtime.
- Its Codex-style workspace includes chat, tools, research/task placeholders, runtime state, and a full settings screen for local API endpoint, provider, model profiles, and tool enablement.
- Non-secret settings persist in the local API. API keys stay out of the database and browser storage; the native app writes them to Windows Credential Manager.
- The desktop now starts and owns a local `agentd` process on `127.0.0.1:8765`; Docker is optional server/development infrastructure rather than a desktop startup dependency.
- Provider calls use the configured OpenAI-compatible endpoint and require the explicit `external_requests` permission in Settings.

## Deliberately deferred

The remaining phases require their own complete slices and evals: full task CRUD + worker/scheduler, Syntarus adapter, research evidence/claim ledgers, daily planning, calendar integration, and developer-authored skills. They are not represented by empty fake modules, per the specification’s implementation rules.

## Verification

`pytest -q` — 4 passed

`npm run build` — completed successfully
