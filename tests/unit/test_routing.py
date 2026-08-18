from agent_core.router import route


def test_reminder_routes_to_productivity():
    result = route("Remind me tomorrow at 9 AM to send the report")
    assert result.mode == "PRODUCTIVITY"
    assert result.expected_output == "REMINDER"
