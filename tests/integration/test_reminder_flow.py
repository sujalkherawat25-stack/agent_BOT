from fastapi.testclient import TestClient
from app.main import app


def test_message_creates_verified_reminder_and_streams_status():
    with TestClient(app) as client:
        response = client.post("/v1/chat/messages", json={"message": "Remind me tomorrow at 9 AM to send the report", "timezone": "Asia/Kolkata"})
    assert response.status_code == 200
    assert "tool.completed" in response.text
    assert "run.completed" in response.text
    assert "send the report" in response.text
