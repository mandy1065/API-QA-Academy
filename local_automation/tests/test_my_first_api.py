"""Copy this template and replace the endpoint/expectations to create new tests."""
import requests


def test_my_first_api():
    # Arrange: choose endpoint and expected outcome.
    url = "https://dummyjson.com/products/1"
    expected_status = 200

    # Act: send the HTTP request.
    response = requests.get(url, timeout=10)

    # Assert: compare actual against expected.
    assert response.status_code == expected_status, response.text
    data = response.json()
    assert data["id"] == 1
