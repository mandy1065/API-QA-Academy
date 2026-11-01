"""Detailed chapter walkthroughs: distinct real-world examples for every module."""
import json
import streamlit as st

# Each row: analogy, step-by-step process, request example, response example, QA assertions, Python snippet.
DETAILS = {
"01": ("A shopping app needs a product price; the API is its agreed way to ask the store.",
["Customer taps a product", "Shopping app sends GET /products/1", "API server routes and validates the request", "Product service retrieves the record", "Server sends HTTP 200 with JSON", "App displays the price"],
"GET https://dummyjson.com/products/1",
'HTTP 200\n{"id":1,"title":"Example product","price":25}',
["Verify the requested ID is returned", "Check the response is JSON", "Try an ID that does not exist"], ""),
"02": ("A mobile app is the client; the server is the program that answers it.",
["Client creates an HTTP request", "DNS/HTTPS connect it to the host", "Server matches the endpoint", "Handler applies rules", "Server sends status and data"],
"GET https://dummyjson.com/users/1",
'HTTP 200\n{"id":1,"firstName":"Example"}',
["Distinguish hostname from path", "Identify the caller and server", "Check /users/999999 for not-found behavior"], ""),
"03": ("A request is the question; the response is the answer.",
["Choose HTTP method", "Add URL and headers", "Add a body only when appropriate", "Send request", "Inspect status, response headers and JSON body"],
"GET /products/1 HTTP/1.1\nHost: dummyjson.com\nAccept: application/json",
'HTTP/1.1 200 OK\nContent-Type: application/json\n\n{"id":1}',
["Verify status and content type", "Compare JSON id with URL id", "Check that an error response is useful"], ""),
"04": ("Reading a product is different from creating, updating or deleting one.",
["GET retrieves", "POST submits a new resource", "PUT replaces/updates as documented", "PATCH partially updates", "DELETE requests removal"],
'POST /products/add\nContent-Type: application/json\n\n{"title":"Demo"}',
'HTTP 201 (illustrative)\n{"id":101,"title":"Demo"}',
["Choose correct method for requirement", "Check creation status per API docs", "Confirm update/delete responses; DummyJSON writes are simulated"], ""),
"05": ("An HTTP status is the server's short summary of the outcome.",
["2xx indicates success", "4xx indicates a request/client problem", "5xx indicates a server failure", "Compare with the expected status for that test"],
"GET /products/999999",
'HTTP 404\n{"message":"Not found"}',
["Valid ID: expect 200", "Missing ID: expect 404", "An expected 404 is a PASS, not automatically a defect"], ""),
"06": ("JSON is the structured data format two applications exchange.",
["Object uses braces and key/value pairs", "Array uses square brackets", "Strings use double quotes", "Numbers and booleans are typed values", "Parse JSON and verify required fields"],
'{"id":1,"title":"Notebook","available":true,"tags":["office"],"discount":null}',
'{"id":1,"title":"Notebook","available":true,"tags":["office"],"discount":null}',
["Validate JSON syntax", "Check id is an integer", "Check tags is an array", "Check missing required fields"], ""),
"07": ("Headers are labels on the message envelope, not the package inside.",
["Accept says what response format is preferred", "Content-Type says what format the sent body uses", "Authorization can carry credentials", "Response headers describe returned data"],
'GET /products/1\nAccept: application/json',
'HTTP 200\nContent-Type: application/json\n\n{"id":1}',
["Inspect Content-Type", "Send Accept header", "Do not expose bearer tokens in logs"], ""),
"08": ("A path selects a resource; a query string filters or paginates it.",
["/users/1 selects user 1", "?limit=5 requests a limited collection", "&skip=5 moves to next page", "Server interprets parameters", "QA validates returned count and metadata"],
"GET /users?limit=5&skip=5",
'HTTP 200\n{"users":[...],"limit":5,"skip":5}',
["Verify limit and skip metadata", "Check returned list size", "Try invalid or boundary values"], ""),
"09": ("Authentication asks who you are; authorization asks what you may do.",
["Client sends login credentials", "Server validates identity", "Server returns access token", "Client sends Bearer token on protected requests", "Server checks permissions"],
'POST /auth/login\nContent-Type: application/json\n\n{"username":"demo","password":"demo"}',
'HTTP 200 (illustrative)\n{"accessToken":"<redacted>"}',
["Valid login", "Invalid password", "Missing token", "Invalid token", "No real secrets in Git"], ""),
"10": ("A QA tester checks that a shopper can retrieve a real product.",
["Write requirement", "Prepare GET endpoint", "Send request", "Record status", "Inspect JSON fields", "Mark PASS/FAIL"],
"GET /products/1",
'HTTP 200\n{"id":1,"title":"Example product"}',
["TC-GET-01: status 200", "TC-GET-02: id equals 1", "TC-GET-03: title is nonempty"], ""),
"11": ("A customer submits a new profile form and the app sends its data to the API.",
["Create JSON payload", "Set Content-Type", "Send POST /users/add", "Inspect returned user fields", "Compare with submitted values"],
'POST /users/add\nContent-Type: application/json\n\n{"firstName":"Alex","age":30}',
'HTTP success\n{"firstName":"Alex","age":30,"id":...}',
["Verify documented creation status", "Verify firstName and age echoed", "Try missing/invalid input if documented"], ""),
"12": ("A profile editor changes a user's last name. PUT and PATCH are two ways to request an update.",
["Read the API documentation and identify PUT vs PATCH behavior", "Choose PUT /users/2 and send a JSON body", "Record actual status and returned JSON", "Choose PATCH /users/2 with only lastName", "Compare changed values and unchanged user ID", "Document that DummyJSON updates are simulated"],
'PUT /users/2\\nContent-Type: application/json\\n\\n{"firstName":"Alex","lastName":"Tester"}\\n\\nPATCH /users/2\\nContent-Type: application/json\\n\\n{"lastName":"QA"}',
'Illustrative HTTP 200\\n{"id":2,"lastName":"QA"}',
["TC-12-01: PUT valid user, verify documented status and updated fields", "TC-12-02: PATCH valid user, verify lastName matches request", "TC-12-03: Check id remains 2", "TC-12-04: Try a nonexistent user and verify documented error"], ""),
"13": ("A customer asks to remove a saved record. The API confirms whether the delete operation was accepted.",
["Identify DELETE /users/1 in the API documentation", "Send DELETE with no JSON body", "Record status code and response headers", "Inspect id, isDeleted and deletedOn fields", "Compare actual result with expected values", "Explain why simulated deletion may not persist on the next GET"],
"DELETE /users/1",
'Illustrative HTTP 200\\n{"id":1,"isDeleted":true,"deletedOn":"<timestamp>"}',
["TC-13-01: DELETE existing user, verify documented success status", "TC-13-02: Verify response id equals 1", "TC-13-03: Verify isDeleted is true", "TC-13-04: Verify deletedOn is present", "TC-13-05: Try invalid user ID and compare documented behavior"], ""),
"14": ("A JSON response can be valid but still contain incorrect data.",
["Parse JSON", "Check required keys", "Validate value types", "Check business values", "Inspect nested objects and arrays"],
"GET /posts/1",
'HTTP 200\n{"id":1,"title":"Example","userId":1}',
["id is integer", "title is nonempty string", "userId exists"], ""),
"15": ("A protected profile should only be accessible with valid credentials.",
["Send login request", "Check successful login", "Capture token", "Call protected endpoint", "Try invalid token"],
"POST /auth/login → GET /auth/me",
'HTTP 200 for valid token; error for invalid token (per contract)',
["Login succeeds", "Token is present", "Protected resource accepts valid token", "Invalid token rejected"], ""),
"16": ("A test case is a repeatable recipe another tester can follow.",
["Write requirement", "Set test ID and preconditions", "Choose input and steps", "State expected status and JSON", "Run and record actual", "Report PASS/FAIL"],
"TC-001 | GET /products/1 | Expected 200 and id=1",
"Actual 200 + id=1 → PASS",
["Positive, negative and boundary cases", "Clear expected results", "Reproducible steps"], ""),
"17": ("Python sends the same request you sent manually.",
["Install requests", "Import requests", "Send GET with timeout", "Inspect response", "Compare with expected"],
"GET /users/1",
'HTTP 200 + JSON user object',
["Use timeout", "Check status", "Check firstName is present"],
'import requests\nr = requests.get("https://dummyjson.com/users/1", timeout=10)\nassert r.status_code == 200\nassert "firstName" in r.json()'),
"18": ("Assertions replace a human reading the response.",
["Write expected result", "Call GET", "Read status and JSON", "Assert ID and type", "Run pytest"],
"GET /users/2",
'HTTP 200 + {"id":2,...}',
["Status 200", "id equals 2", "firstName is string"],
'import requests\ndef test_get_user():\n    r = requests.get("https://dummyjson.com/users/2", timeout=10)\n    assert r.status_code == 200\n    assert r.json()["id"] == 2'),
"19": ("A negative test passes when the server rejects an invalid resource correctly.",
["Choose positive and negative IDs", "Set expected statuses", "Send both requests", "Assert exact status"],
"GET /users/999999",
"HTTP 404",
["Positive 200", "Missing user 404"],
'import requests\ndef test_missing_user():\n    r = requests.get("https://dummyjson.com/users/999999", timeout=10)\n    assert r.status_code == 404'),
"20": ("A 200 response can still contain the wrong JSON.",
["Parse once", "Assert required keys", "Assert types", "Assert meaningful values"],
"GET /posts/1",
'HTTP 200 + {"id":1,"title":"..."}',
["id == 1", "title is string", "title is nonempty"],
'import requests\ndef test_post_json():\n    r = requests.get("https://dummyjson.com/posts/1", timeout=10)\n    assert r.status_code == 200\n    data = r.json()\n    assert data["id"] == 1\n    assert isinstance(data["title"], str)'),
"21": ("Automate a create request by sending a Python dictionary as JSON.",
["Create payload dict", "POST with json=payload", "Check status", "Assert echoed fields", "Do not assume persistence"],
"POST /users/add",
'HTTP success + new user JSON',
["Returned firstName matches", "Returned id exists"],
'import requests\ndef test_add_user():\n    payload = {"firstName":"Alex","age":30}\n    r = requests.post("https://dummyjson.com/users/add", json=payload, timeout=10)\n    assert r.status_code == 201\n    assert r.json()["firstName"] == payload["firstName"]'),
"22": ("PATCH modifies selected fields and the test checks the change.",
["Build payload", "Send PATCH", "Assert status", "Assert updated field", "Assert identity"],
"PATCH /users/2",
'HTTP 200 + updated user',
["lastName updated", "id remains 2"],
'import requests\ndef test_patch_user():\n    r = requests.patch("https://dummyjson.com/users/2", json={"lastName":"QA"}, timeout=10)\n    assert r.status_code == 200\n    assert r.json()["lastName"] == "QA"'),
"23": ("Deletion tests validate the server's response, not a UI message.",
["Send DELETE", "Check status", "Parse JSON", "Check deletion flag"],
"DELETE /users/1",
'HTTP 200 + isDeleted true',
["isDeleted true", "id is correct"],
'import requests\ndef test_delete_user():\n    r = requests.delete("https://dummyjson.com/users/1", timeout=10)\n    assert r.status_code == 200\n    assert r.json()["isDeleted"] is True'),
"24": ("Headers can be sent and validated from Python.",
["Create headers dict", "Send request", "Inspect response headers", "Assert content type"],
"GET /test",
"HTTP response with Content-Type",
["Accept sent", "Content-Type includes JSON"],
'import requests\ndef test_headers():\n    r = requests.get("https://dummyjson.com/test", headers={"Accept":"application/json"}, timeout=10)\n    assert r.status_code == 200\n    assert "application/json" in r.headers.get("Content-Type","")'),
"25": ("Pagination tests check that the API honors limit and skip.",
["Set params dictionary", "Send GET", "Parse JSON", "Assert limit and skip", "Check list size"],
"GET /users?limit=5&skip=5",
'HTTP 200 + limit=5 skip=5',
["limit == 5", "skip == 5", "users list length <= 5"],
'import requests\ndef test_pagination():\n    r = requests.get("https://dummyjson.com/users", params={"limit":5,"skip":5}, timeout=10)\n    assert r.status_code == 200\n    data = r.json()\n    assert data["limit"] == 5\n    assert data["skip"] == 5'),
"26": ("Automated login captures a token for later API calls.",
["Send training credentials", "Assert success", "Extract accessToken", "Keep token out of logs"],
"POST /auth/login",
'HTTP 200 + accessToken',
["Status success", "Nonempty token"],
'import requests\ndef test_login():\n    r = requests.post("https://dummyjson.com/auth/login", json={"username":"emilys","password":"emilyspass"}, timeout=10)\n    assert r.status_code == 200\n    assert r.json().get("accessToken")'),
"27": ("The second request uses the token returned by login.",
["Login", "Capture token", "Create Authorization header", "GET /auth/me", "Assert username"],
"GET /auth/me with Bearer token",
'HTTP 200 + authenticated profile',
["Valid token accepted", "Correct username", "Invalid token rejected"],
'import requests\ndef test_auth_me():\n    login = requests.post("https://dummyjson.com/auth/login", json={"username":"emilys","password":"emilyspass"}, timeout=10)\n    assert login.status_code == 200\n    token = login.json()["accessToken"]\n    r = requests.get("https://dummyjson.com/auth/me", headers={"Authorization":f"Bearer {token}"}, timeout=10)\n    assert r.status_code == 200'),
"28": ("Negative automation deliberately uses invalid input.",
["Choose invalid resource", "Define expected error", "Send request", "Assert documented status"],
"GET /users/999999",
"HTTP 404",
["Missing resource returns 404", "Unexpected 500 fails test"],
'import requests\ndef test_unknown_user():\n    r = requests.get("https://dummyjson.com/users/999999", timeout=10)\n    assert r.status_code == 404'),
"29": ("pytest finds test_ functions and reports failures automatically.",
["Install pytest", "Create test_products.py", "Write test_ function", "Run python -m pytest -v", "Read PASSED/FAILED"],
"python -m pytest -v",
"tests/test_products.py::test_product PASSED",
["Test discovery", "Assertion output"],
'import requests\ndef test_product():\n    r = requests.get("https://dummyjson.com/products/1", timeout=10)\n    assert r.status_code == 200'),
"30": ("Fixtures prepare reusable objects for tests.",
["Define @pytest.fixture", "Create session", "Inject fixture as argument", "Reuse in tests"],
"conftest.py → tests/test_users.py",
"Two tests share a session fixture",
["Fixture reused", "Session closed after test"],
'import pytest\nimport requests\n@pytest.fixture\ndef api():\n    with requests.Session() as session:\n        yield session\n\ndef test_user(api):\n    r = api.get("https://dummyjson.com/users/1", timeout=10)\n    assert r.status_code == 200'),
"31": ("Parametrization runs one test design against multiple input rows.",
["Define cases", "Add @pytest.mark.parametrize", "Use arguments in test", "Read separate results"],
"IDs 1, 2, 3",
"3 tests PASSED",
["Each input independently checked", "Returned user ID matches each parameter", "Each case reports its own PASS or FAIL"],
'import pytest\nimport requests\n@pytest.mark.parametrize("user_id", [1,2,3])\ndef test_user(user_id):\n    r = requests.get(f"https://dummyjson.com/users/{user_id}", timeout=10)\n    assert r.status_code == 200\n    assert r.json()["id"] == user_id'),
"32": ("API client helpers send requests; test functions decide PASS/FAIL.",
["Define get_user helper", "Call helper from test", "Assert response", "Reuse helper in another test"],
"client.get_user(1)",
"Response passed to test assertions",
["No duplicated URLs", "Assertions stay in tests"],
'import requests\ndef get_user(user_id):\n    return requests.get(f"https://dummyjson.com/users/{user_id}", timeout=10)\n\ndef test_user():\n    r = get_user(1)\n    assert r.status_code == 200'),
"33": ("A network can be slow or unavailable, so tests need bounded waits.",
["Set timeout", "Catch meaningful network errors only when necessary", "Report failure clearly", "Avoid swallowing assertion failures"],
"GET /users/1 timeout=10",
"Pass or clear network exception",
["Timeout present", "Failure not hidden"],
'import requests\ndef test_timeout_safe():\n    r = requests.get("https://dummyjson.com/users/1", timeout=10)\n    assert r.status_code == 200'),
"34": ("Separate data from tests so cases are easier to maintain.",
["Create test payload", "Load from fixture or JSON", "Pass to API client", "Assert returned values", "Never commit real secrets"],
"data/user.json + tests/test_users.py",
"Payload reused across tests",
["No hardcoded secrets", "Expected values checked"],
'import pytest\nimport requests\n@pytest.fixture\ndef user_payload():\n    return {"firstName":"Alex","age":30}\n\ndef test_create(user_payload):\n    r = requests.post("https://dummyjson.com/users/add", json=user_payload, timeout=10)\n    assert r.status_code == 201\n    assert r.json()["firstName"] == user_payload["firstName"]'),
"35": ("A small framework separates configuration, clients, fixtures and tests.",
["Create tests/ folder", "Create clients/ helpers", "Add conftest.py fixtures", "Add pytest.ini", "Run all tests"],
"tests/ + clients/ + conftest.py + pytest.ini",
"pytest -v runs full suite",
["Reusable API calls", "Clear failures", "No shared mutable test state"],
'from pathlib import Path\n# Example layout:\n# tests/test_users.py\n# clients/users_client.py\n# conftest.py\n# pytest.ini'),
"36": ("Final project: design manual cases and turn them into a repeatable suite.",
["Write API requirements", "Design 12+ positive/negative cases", "Implement GET/POST/PATCH/DELETE", "Add auth, fixtures and parameters", "Run suite and report results"],
"python -m pytest -v",
"12+ cases with documented expected results",
["Positive and negative coverage", "Fixtures and parameterization", "Clear report and limitations"],
'## Final checklist\n# 12+ tests\n# GET, POST, PATCH, DELETE\n# Auth + negative cases\n# Fixtures + parametrization\n# pytest -v report'),
}

def diagram(stage, mid):
    if stage == "API Foundations":
        if mid in {"06", "07", "08"}:
            labels = ["Client input", "HTTP request", "API server", "JSON response"]
        elif mid == "09":
            labels = ["Login", "Token", "Protected API", "Authorized response"]
        else:
            labels = ["Shopping client", "API endpoint", "Server + rules", "Data source"]
    elif stage == "Manual API Testing":
        labels = ["Requirement", "Test steps", "Send request", "Expected vs actual"]
    elif stage == "API Automation":
        labels = ["Python test", "requests call", "API response", "assert checks"]
    else:
        labels = ["pytest suite", "Fixture / client", "API response", "Report"]
    a,b,c,d = [x.replace('"',"'") for x in labels]
    graph = f'digraph {{ rankdir=LR; node [shape=box style="rounded,filled" fillcolor="#eff6ff" color="#2563eb"]; A [label="{a}"]; B [label="{b}"]; C [label="{c}"]; D [label="{d}"]; A -> B -> C -> D; }}'
    st.graphviz_chart(graph, use_container_width=True)

def render_detail(module):
    mid = module["id"]
    analogy, steps, request, response, checks, code = DETAILS[mid]
    st.markdown("#### 1. Real-world story")
    st.markdown(analogy)
    st.markdown("#### 2. Visual workflow")
    diagram(module["stage"], mid)
    st.markdown("#### 3. Follow each step")
    for i, step in enumerate(steps, 1):
        st.markdown(f"**Step {i}:** {step}")
    st.markdown("#### 4. Worked example — request / action")
    st.code(request, language="http" if mid not in {"29","35","36"} else "text")
    st.markdown("**Example response / expected outcome**")
    st.code(response, language="text")
    st.caption("Response snippets are illustrative unless explicitly verified live. The API Lab can show actual DummyJSON responses.")
    st.markdown("#### 5. QA test cases — what would you validate?")
    for i, check in enumerate(checks, 1):
        st.markdown(f"- **TC-{mid}-{i:02d}:** {check}")
    st.markdown("#### 6. Practice exercise")
    st.info(module["assignment"])
    if code:
        st.markdown("#### 7. Python automation example")
        st.code(code, language="python")
        st.markdown("**Run in VS Code:** save the example as `test_example.py` (if it contains a `test_` function), install `requests pytest`, then run `python -m pytest -v`. The repository's `local_automation/README.md` explains setup.")
    if mid == "05":
        status = st.selectbox("Choose actual HTTP status", [200,404,500], key="detail_status_05")
        st.markdown("**Expected:** 404 for a missing product.")
        if st.button("Check expected vs actual", key="detail_check_05"):
            (st.success if status == 404 else st.error)("PASS" if status == 404 else "FAIL: actual differs from expected")
    if mid == "04":
        method = st.selectbox("What action are you performing?", ["Read a product","Create a product","Partially edit a product","Delete a product"], key="detail_method_04")
        st.code({"Read a product":"GET","Create a product":"POST","Partially edit a product":"PATCH","Delete a product":"DELETE"}[method], language="http")
    st.markdown("#### 8. What you should be able to explain")
    st.markdown(f"After this chapter, explain **{module['title']}** in your own words, describe the example above, and identify at least two checks a QA engineer should make.")
