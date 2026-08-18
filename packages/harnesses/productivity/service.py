import hashlib
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from storage.db import AgentRunRow, AuditEventRow, ReminderRow


def idempotency_key(user_id: str, message: str, trigger_at: datetime) -> str:
    return hashlib.sha256(f"{user_id}|{message.strip().casefold()}|{trigger_at.isoformat()}".encode()).hexdigest()


async def create_and_verify_reminder(session: AsyncSession, *, user_id: str, run: AgentRunRow, message: str, trigger_at: datetime, tz: str) -> ReminderRow:
    key = idempotency_key(user_id, message, trigger_at)
    existing = await session.scalar(select(ReminderRow).where(ReminderRow.user_id == user_id, ReminderRow.idempotency_key == key))
    if existing:
        return existing
    reminder = ReminderRow(user_id=user_id, message=message, trigger_at=trigger_at, timezone=tz, idempotency_key=key)
    session.add(reminder)
    session.add(AuditEventRow(user_id=user_id, run_id=run.id, event_type="REMINDER_CREATED", payload_json={"reminder_id": reminder.id, "trigger_at": trigger_at.isoformat()}))
    await session.flush()
    verified = await session.scalar(select(ReminderRow).where(ReminderRow.id == reminder.id))
    if verified is None or verified.trigger_at != trigger_at:
        raise RuntimeError("Reminder postcondition verification failed")
    run.status = "completed"
    run.completed_at = datetime.now(timezone.utc)
    session.add(AuditEventRow(user_id=user_id, run_id=run.id, event_type="RUN_COMPLETED", payload_json={"result": "reminder_created"}))
    await session.commit()
    return verified
