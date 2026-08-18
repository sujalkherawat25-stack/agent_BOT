import re
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class ReminderIntent:
    title: str
    trigger_at: datetime
    timezone: str


def parse_reminder(message: str, timezone: str, now: datetime | None = None) -> ReminderIntent:
    """Small deterministic parser for the supported first-slice reminder grammar."""
    tz = ZoneInfo(timezone)
    current = (now or datetime.now(tz)).astimezone(tz)
    match = re.search(r"remind me\s+(?:(tomorrow|today)\s+)?(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s+to\s+(.+)", message, re.I)
    if not match:
        raise ValueError("Please use a time, for example: Remind me tomorrow at 9 AM to send the report.")
    day, hour_text, minute_text, meridiem, title = match.groups()
    hour, minute = int(hour_text), int(minute_text or 0)
    if meridiem:
        if hour < 1 or hour > 12:
            raise ValueError("Use an hour between 1 and 12 with AM or PM.")
        hour = hour % 12 + (12 if meridiem.lower() == "pm" else 0)
    elif hour > 23:
        raise ValueError("Use a 24-hour time between 00:00 and 23:59.")
    target_date = current.date() + timedelta(days=1 if day and day.lower() == "tomorrow" else 0)
    target = datetime.combine(target_date, time(hour, minute), tzinfo=tz)
    if day is None and target <= current:
        target += timedelta(days=1)
    if target <= current:
        raise ValueError("The reminder must be in the future.")
    return ReminderIntent(title=title.strip().rstrip("."), trigger_at=target.astimezone(ZoneInfo("UTC")), timezone=timezone)
