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


def test_list_titles_multiple_ordering():
    response = client.get("/api/titles?_sort=id,title_number&_order=desc,desc&_page=1")
    assert response.status_code == 200


def test_list_titles_multiple_ordering_query_validation():
    response = client.get("/api/titles?_sort=id&_limit=3&_page=1&_order=UP")
    assert response.status_code == 422
