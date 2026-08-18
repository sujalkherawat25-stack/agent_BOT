from datetime import datetime
from zoneinfo import ZoneInfo
import pytest
from harnesses.productivity.intent import parse_reminder


def test_parses_tomorrow_reminder_in_user_timezone():
    intent = parse_reminder("Remind me tomorrow at 9 AM to send the report", "Asia/Kolkata", datetime(2026, 8, 18, 12, tzinfo=ZoneInfo("Asia/Kolkata")))
    assert intent.title == "send the report"
    assert intent.trigger_at == datetime(2026, 8, 19, 3, 30, tzinfo=ZoneInfo("UTC"))


def test_rejects_missing_time():
    with pytest.raises(ValueError, match="Please use a time"):
        parse_reminder("Remind me to send the report", "UTC")
