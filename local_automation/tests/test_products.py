"""Run with: python -m pytest -v"""
import pytest
import requests

BASE_URL = "https://dummyjson.com"


@pytest.fixture(scope="session")
def api_session():
    with requests.Session() as session:
        session.headers.update({"Accept": "application/json"})
        yield session


@pytest.mark.parametrize("product_id,expected_status", [(1, 200), (999999, 404)])
def test_get_product_status(api_session, product_id, expected_status):
    response = api_session.get(f"{BASE_URL}/products/{product_id}", timeout=10)
    assert response.status_code == expected_status, response.text


def test_get_product_fields(api_session):
    response = api_session.get(f"{BASE_URL}/products/1", timeout=10)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert isinstance(body["title"], str)
    assert body["title"].strip()


def test_search_returns_list(api_session):
    response = api_session.get(f"{BASE_URL}/products/search", params={"q": "phone"}, timeout=10)
    assert response.status_code == 200
    assert isinstance(response.json()["products"], list)
