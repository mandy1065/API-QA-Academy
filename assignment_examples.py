"""Runnable teaching examples aligned to each API automation assignment.

These are learning references, not a replacement for integration tests.
Advanced pytest examples must run in VS Code, not inside Streamlit's
restricted in-process runner.
"""
EXAMPLES = {
"17": '''import requests

response = requests.get("https://dummyjson.com/users/1", timeout=10)
assert response.status_code == 200
data = response.json()
print("Status:", response.status_code)
print("First name:", data["firstName"])
''',
"18": '''import requests

def test_get_user_2():
    response = requests.get("https://dummyjson.com/users/2", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2
    assert isinstance(data["firstName"], str)
    assert data["firstName"].strip()
''',
"19": '''import requests

def test_existing_user():
    response = requests.get("https://dummyjson.com/users/1", timeout=10)
    assert response.status_code == 200

def test_missing_user():
    response = requests.get("https://dummyjson.com/users/999999", timeout=10)
    assert response.status_code == 404
''',
"20": '''import requests

def test_post_json_fields():
    response = requests.get("https://dummyjson.com/posts/1", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["id"] == 1
    assert isinstance(data["title"], str)
    assert len(data["title"]) > 0
    assert isinstance(data["userId"], int)
''',
"21": '''import requests

def test_create_user():
    payload = {"firstName": "Alex", "age": 30}
    response = requests.post("https://dummyjson.com/users/add", json=payload, timeout=10)
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["firstName"] == payload["firstName"]
    assert data["age"] == payload["age"]
# DummyJSON simulates creation: the new user is not persisted.
''',
"22": '''import requests

def test_patch_user():
    payload = {"lastName": "QA"}
    response = requests.patch("https://dummyjson.com/users/2", json=payload, timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2
    assert data["lastName"] == payload["lastName"]
# DummyJSON simulates updates.
''',
"23": '''import requests

def test_delete_user():
    response = requests.delete("https://dummyjson.com/users/1", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["isDeleted"] is True
    assert "deletedOn" in data
# DummyJSON simulates deletion.
''',
"24": '''import requests

def test_json_headers():
    response = requests.get(
        "https://dummyjson.com/test",
        headers={"Accept": "application/json"},
        timeout=10,
    )
    assert response.status_code == 200
    assert "application/json" in response.headers.get("Content-Type", "")
''',
"25": '''import requests

def test_pagination():
    response = requests.get(
        "https://dummyjson.com/users",
        params={"limit": 5, "skip": 5},
        timeout=10,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 5
    assert data["skip"] == 5
    assert len(data["users"]) <= 5
''',
"26": '''import requests

def test_login():
    response = requests.post(
        "https://dummyjson.com/auth/login",
        json={"username": "emilys", "password": "emilyspass"},
        timeout=10,
    )
    assert response.status_code == 200
    assert response.json().get("accessToken")
    # Never print or commit real credentials or tokens.
''',
"27": '''import requests

def test_protected_user():
    login = requests.post(
        "https://dummyjson.com/auth/login",
        json={"username": "emilys", "password": "emilyspass"},
        timeout=10,
    )
    assert login.status_code == 200
    token = login.json()["accessToken"]
    response = requests.get(
        "https://dummyjson.com/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert response.status_code == 200
    assert response.json()["username"] == "emilys"

def test_invalid_token():
    response = requests.get(
        "https://dummyjson.com/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
        timeout=10,
    )
    assert response.status_code in (401, 403)
''',
"28": '''import requests

def test_missing_user():
    response = requests.get("https://dummyjson.com/users/999999", timeout=10)
    assert response.status_code == 404

def test_missing_product():
    response = requests.get("https://dummyjson.com/products/999999", timeout=10)
    assert response.status_code == 404

def test_invalid_token():
    response = requests.get(
        "https://dummyjson.com/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
        timeout=10,
    )
    assert response.status_code in (401, 403)
''',
"29": '''import requests

def test_get_user():
    r = requests.get("https://dummyjson.com/users/1", timeout=10)
    assert r.status_code == 200
    assert r.json()["id"] == 1

def test_missing_user():
    r = requests.get("https://dummyjson.com/users/999999", timeout=10)
    assert r.status_code == 404

def test_get_product():
    r = requests.get("https://dummyjson.com/products/1", timeout=10)
    assert r.status_code == 200
    assert r.json()["id"] == 1
''',
"30": '''import pytest
import requests

@pytest.fixture
def base_url():
    return "https://dummyjson.com"

def test_user(base_url):
    r = requests.get(f"{base_url}/users/1", timeout=10)
    assert r.status_code == 200

def test_product(base_url):
    r = requests.get(f"{base_url}/products/1", timeout=10)
    assert r.status_code == 200
''',
"31": '''import pytest
import requests

@pytest.mark.parametrize("user_id", [1, 2, 3])
def test_user_id(user_id):
    r = requests.get(f"https://dummyjson.com/users/{user_id}", timeout=10)
    assert r.status_code == 200
    assert r.json()["id"] == user_id
''',
"32": '''import requests

def get_user(user_id):
    return requests.get(f"https://dummyjson.com/users/{user_id}", timeout=10)

def get_users(limit=5):
    return requests.get("https://dummyjson.com/users", params={"limit": limit}, timeout=10)

def test_user():
    assert get_user(1).json()["id"] == 1

def test_users():
    r = get_users(5)
    assert r.status_code == 200
    assert len(r.json()["users"]) <= 5
''',
"33": '''import requests

def get_user(user_id, timeout=10):
    return requests.get(f"https://dummyjson.com/users/{user_id}", timeout=timeout)

def test_user_with_timeout():
    response = get_user(1)
    assert response.status_code == 200
''',
"34": '''import pytest
import requests

@pytest.fixture
def user_payload():
    return {"firstName": "Alex", "age": 30}

@pytest.fixture
def second_payload():
    return {"firstName": "Sam", "age": 31}

@pytest.mark.parametrize("payload_name", ["user_payload", "second_payload"])
def test_create_users(payload_name, request):
    payload = request.getfixturevalue(payload_name)
    r = requests.post("https://dummyjson.com/users/add", json=payload, timeout=10)
    assert r.status_code == 201
    assert r.json()["firstName"] == payload["firstName"]
''',
}
