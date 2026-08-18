# Memento desktop

This Tauri 2 application is the lightweight Windows desktop shell for the Personal Agent. It uses the system WebView rather than bundling Chromium, which keeps startup, RAM, and disk overhead low.

- Frontend assets are statically exported from `apps/web`.
- The local Agent API target is configurable in the app settings.
- Provider API keys are stored through Windows Credential Manager via the native Rust `keyring` crate. They are never written to the API settings table, `.env`, or browser storage.

## Develop

Start the API first (`docker compose up -d` from the repository root), then:

```powershell
cd apps/desktop
npm install
npm run dev
```

## Build the installer

```powershell
npm run build
```

The Windows installer is written under `apps/desktop/src-tauri/target/release/bundle/nsis/`.
