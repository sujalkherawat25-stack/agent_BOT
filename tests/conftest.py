import os

# Tests must never read the Docker-only `postgres` hostname from a developer's .env.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_agent.db"
