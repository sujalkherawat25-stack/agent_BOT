from fastapi.testclient import TestClient
from app.main import app


def test_task_crud_and_memory_write_read():
    with TestClient(app) as client:
        task = client.post("/v1/tasks?user_id=slice-test", json={"title": "Ship the desktop build", "priority": "high"})
        assert task.status_code == 200
        task_id = task.json()["id"]
        updated = client.patch(f"/v1/tasks/{task_id}?user_id=slice-test", json={"status": "done"})
        assert updated.status_code == 200
        assert updated.json()["status"] == "done"
        memory = client.post("/v1/memory?user_id=slice-test", json={"content": "I prefer concise status updates", "importance": 3})
        assert memory.status_code == 200
        recalled = client.get("/v1/memory?user_id=slice-test&query=concise")
        assert recalled.status_code == 200
        assert recalled.json()[0]["content"] == "I prefer concise status updates"


def test_research_requires_explicit_permissions():
    with TestClient(app) as client:
        response = client.post("/v1/research?user_id=research-test", json={"query": "test", "urls": ["https://example.com"]})
        assert response.status_code == 403
