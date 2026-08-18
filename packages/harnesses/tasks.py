from datetime import datetime, timezone

from sqlalchemy import select

from storage.db import SessionLocal, TaskRow


async def tick_tasks() -> int:
    now = datetime.now(timezone.utc)
    async with SessionLocal() as db:
        rows = list(await db.scalars(select(TaskRow).where(TaskRow.status == "open", TaskRow.due_at.is_not(None), TaskRow.due_at <= now)))
        for row in rows:
            row.status = "in_progress"
        if rows:
            await db.commit()
        return len(rows)
