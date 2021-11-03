from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_titles_detail():
    response = client.get("/api/titles/1")
    assert response.status_code == 200
    assert all(
        key in response.json()
        for key in ("content", "id", "title_number", "title_class")
    )


def test_title_detail_path_validation():
    response = client.get("/api/titles/sdf")
    assert response.status_code == 422


def test_list_titles():
    response = client.get("/api/titles/")
    assert response.status_code == 200

