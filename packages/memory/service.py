from datetime import datetime, timezone
import re

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from storage.db import MemoryRow


def _terms(text: str) -> list[str]:
    stop = {"the", "and", "that", "with", "what", "when"}
    return [term for term in re.findall(r"[\w'-]{3,}", text.casefold()) if term not in stop][:8]


async def recall_memories(db: AsyncSession, user_id: str, query: str, limit: int = 5) -> list[MemoryRow]:
    terms = _terms(query)
    if not terms:
        return []
    rows = list(await db.scalars(select(MemoryRow).where(MemoryRow.user_id == user_id, or_(*(MemoryRow.content.ilike(f"%{term}%") for term in terms))).order_by(MemoryRow.importance.desc(), MemoryRow.created_at.desc()).limit(limit)))
    now = datetime.now(timezone.utc)
    for row in rows:
        row.last_accessed_at = now
    return rows


async def remember(db: AsyncSession, user_id: str, content: str, conversation_id: str | None = None, importance: int = 1) -> MemoryRow:
    row = MemoryRow(user_id=user_id, content=content.strip(), source_conversation_id=conversation_id, importance=importance)
    db.add(row)
    await db.flush()
    return row


def memory_candidate(message: str) -> tuple[str, int] | None:
    normalized = message.strip()
    lowered = normalized.casefold()
    signals = ("remember", "my ", "i am ", "i'm ", "i like ", "i prefer ", "i work ")
    if len(normalized) <= 500 and any(signal in lowered for signal in signals):
        return normalized, 3 if "remember" in lowered else 2
    return None
