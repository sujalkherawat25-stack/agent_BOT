# Personal Agent

An evidence-first, safety-gated personal AI agent. This repository implements the first vertical slice from `PERSONAL_AGENT_IMPLEMENTATION_SPEC.md`: a message becomes an observable productivity run that deterministically creates and verifies a reminder.

## What works

- FastAPI API with health, conversations, chat/SSE events, tasks, reminders, runs, approvals, and memory routes.
- Durable Postgres models for users, conversations, messages, runs, reminders, tasks, audit events, and approvals.
- Deterministic reminder intent parsing, timezone-aware scheduling, idempotency, postcondition verification, and user-legible SSE activity.
- Provider-neutral model boundary plus an xAI Responses API adapter. The reminder path remains usable without an API key.
- Next.js workspace UI, Docker Compose, unit/integration tests, and GitHub Actions CI.

## Run it

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open http://localhost:3000 for the browser preview, or use the lightweight native control app in `apps/desktop`. The API docs are at http://localhost:8000/docs.

To use xAI, add `XAI_API_KEY` to `.env`; provider calls remain isolated in `packages/models/`.

## Architecture

`apps/api` is the HTTP boundary. `packages/agent_core` owns routing and execution, `packages/harnesses/productivity` owns deterministic productivity intent and mutations, `packages/models` owns provider adapters, and `packages/storage` owns operational state. Semantic memory is deliberately not used as task/reminder state.

`apps/desktop` is a Tauri 2 Windows shell: it uses the system WebView rather than Electron, presents a Codex-style workspace, and keeps provider secrets in Windows Credential Manager.

## Next slices

The repository is intentionally a complete initial vertical slice rather than empty scaffolding for every future phase. The next implementation order is task CRUD/scheduler worker, then the Syntarus adapter, then the evidence-ledger research harness.
