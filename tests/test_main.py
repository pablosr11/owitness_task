from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_titles():
    response = client.get("/api/titles/")
    assert response.status_code == 200

