"""Local Memento runtime launcher owned by the desktop shell."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages"))
sys.path.insert(0, str(ROOT / "apps" / "api"))
data_dir = Path(os.environ.get("MEMENTO_DATA_DIR", Path.home() / "AppData" / "Local" / "Memento"))
data_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{(data_dir / 'agent.db').as_posix()}")
os.environ.setdefault("CORS_ORIGINS_RAW", "http://localhost:3000,http://127.0.0.1:8765")

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=int(os.environ.get("MEMENTO_PORT", "8765")), log_level="warning")
