# Memento local runtime

`agentd.py` is the desktop-owned backend. Tauri starts it on `127.0.0.1:8765`,
keeps SQLite data in `%LOCALAPPDATA%\Memento`, and stops it when the app closes.
Docker Compose remains available for server/development mode only.
