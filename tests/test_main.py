from tests.conftest import title_factory


def test_titles_detail(client, session):
    title_factory(session)

    response = client.get("/api/titles/1")
    assert response.status_code == 200
    assert all(
        key in response.json()
        for key in ("content", "id", "title_number", "title_class")
    )


def test_titles_detail_unknown(client, session):
    response = client.get("/api/titles/1")
    assert response.status_code == 404


def test_title_detail_path_validation(client):
    response = client.get("/api/titles/sdf")
    assert response.status_code == 422


def test_list_titles(client, session):
    title_factory(session)
    response = client.get("/api/titles/")
    assert response.status_code == 200


def test_list_titles_no_titltes_returns_404(client):
    response = client.get("/api/titles/")
    assert response.status_code == 404


def test_list_titles_with_title_class(client, session):
    title_factory(session)
    response = client.get("/api/titles?title_class=Freehold")
    assert response.status_code == 200


def test_list_titles_multiple_ordering(client, session):
    title_factory(session)
    title_factory(session)
    response = client.get("/api/titles?_sort=id,title_number&_order=desc,desc&_page=0")
    assert response.status_code == 200


def test_list_titles_multiple_ordering_query_validation(client):
    response = client.get("/api/titles?_sort=id&_limit=3&_page=1&_order=UP")
    assert response.status_code == 422


def test_list_titles_multiple_sort_query_validation(client):
    response = client.get("/api/titles?_sort=ids&_limit=3&_page=1")
    assert response.status_code == 422


def test_list_titles_multiple_ordering_query_number_validation(client):
    response = client.get("/api/titles?_sort=id&_limit=3&_page=1&_order=asc,desc")
    assert response.status_code == 400
