"""Structured beginner path: foundations -> manual QA -> pytest automation."""
import json
import re
import requests
import streamlit as st
from api_foundations import show_foundations

BASE = "https://dummyjson.com"
CASES = [
    {"id":"TC-001","title":"Existing product","path":"/products/1","status":200,"field":"id","expected":1,"kind":"Positive"},
    {"id":"TC-002","title":"Missing product","path":"/products/999999","status":404,"field":None,"expected":None,"kind":"Negative"},
    {"id":"TC-003","title":"Search products","path":"/products/search?q=phone","status":200,"field":"products","expected":"list","kind":"Positive"},
]


def evaluate(response, case):
    checks = {"HTTP status matches expected": response.status_code == case["status"]}
    try:
        payload = response.json()
    except ValueError:
        payload = response.text
    if case["field"]:
        value = payload.get(case["field"]) if isinstance(payload, dict) else None
        checks["JSON field matches expected"] = (
            isinstance(value, list) if case["expected"] == "list" else value == case["expected"]
        )
    return checks, payload


def generate_test(case, test_name):
    if not re.fullmatch(r"test_[a-z][a-z0-9_]{0,55}", test_name):
        raise ValueError("Test name must start with test_ and contain only lowercase letters, numbers and underscores.")
    lines = [
        "import requests", "", "",
        f"def {test_name}():",
        "    # Arrange: endpoint and expected response",
        f"    url = {BASE + case['path']!r}",
        f"    expected_status = {case['status']}",
        "    # Act: send request",
        "    response = requests.get(url, timeout=10)",
        "    # Assert: compare actual against expected",
        "    assert response.status_code == expected_status, response.text",
    ]
    if case["field"]:
        lines += ["    data = response.json()"]
        if case["expected"] == "list":
            lines += [f"    assert isinstance(data[{case['field']!r}], list)"]
        else:
            lines += [f"    assert data[{case['field']!r}] == {case['expected']!r}"]
    return "\n".join(lines) + "\n"


def show_manual():
    st.header("🧪 Stage 2 — Manual API Testing")
    st.markdown("**Goal:** Understand the requirement, design a test case, send a request, and compare expected vs actual. No Python required.")
    st.subheader("Step 1 · Start from a business requirement")
    st.info("As a shopper, I can open an existing product and see its details. If the product ID does not exist, the API should return a documented not-found response.")
    st.markdown("""
A QA engineer translates this into **test conditions**:
- **Positive:** a valid product ID returns success and the correct product.
- **Negative:** a nonexistent product ID returns an expected error.
- **Data checks:** correct ID, required fields, correct JSON types.
- **Nonfunctional checks:** response time, permissions and error handling (as applicable).

**Test case fields:** ID, title, precondition, HTTP method, URL, steps, expected status, expected JSON, actual result and PASS/FAIL.
""")
    st.subheader("Step 2 · Read three example test cases")
    st.dataframe([{
        "Test ID":c["id"], "Type":c["kind"], "Scenario":c["title"],
        "Method":"GET", "Endpoint":c["path"], "Expected status":c["status"],
        "Expected body check":f"{c['field']} = {c['expected']}" if c["field"] else "Not-found error"
    } for c in CASES], hide_index=True, use_container_width=True)
    chosen = st.selectbox("Step 3 · Pick a test case", [c["id"]+" — "+c["title"] for c in CASES], key="manual_case")
    case = CASES[[c["id"] for c in CASES].index(chosen.split(" — ")[0])]
    st.markdown(f"**Precondition:** Internet access and the public DummyJSON training API.  \n**Request:** `GET {BASE}{case['path']}`  \n**Expected status:** `{case['status']}`")
    st.markdown("**Steps:** 1. Prepare endpoint → 2. Send GET → 3. Capture response → 4. Compare status and JSON → 5. Record result.")
    if st.button("▶ Execute selected manual test", type="primary", key="manual_execute"):
        try:
            response = requests.get(BASE + case["path"], timeout=10)
            checks, payload = evaluate(response, case)
            st.session_state.manual_result = {
                "case":case["id"], "actual_status":response.status_code, "checks":checks,
                "body":payload, "url":response.url,
            }
        except requests.RequestException as exc:
            st.session_state.manual_result = {"case":case["id"], "error":str(exc)}
    result = st.session_state.get("manual_result")
    if result and result["case"] == case["id"]:
        if "error" in result:
            st.error("Could not complete request: " + result["error"])
        else:
            st.metric("Actual HTTP status", result["actual_status"])
            for label, passed in result["checks"].items():
                (st.success if passed else st.error)(f"{'PASS' if passed else 'FAIL'} — {label}")
            with st.expander("View actual JSON / response"):
                st.json(result["body"])
            if all(result["checks"].values()):
                st.success("Overall PASS: actual results match the test case expectations.")
            else:
                st.error("Overall FAIL: compare actual and expected, then investigate.")
    st.subheader("Step 4 · Write your own test case")
    title = st.text_input("Test title", "Verify product 1 returns the correct ID", key="manual_title")
    expected = st.text_area("Expected result", "HTTP 200; response JSON has id = 1", key="manual_expected")
    steps = st.text_area("Manual test steps", "1. Send GET /products/1\n2. Inspect status code\n3. Inspect JSON id\n4. Compare actual with expected", key="manual_steps")
    st.download_button("↓ Download my test case (JSON)", json.dumps({"title":title,"steps":steps,"expected":expected},indent=2), "my_api_test_case.json", "application/json", key="manual_export")
    st.caption("Next: convert the same expected-vs-actual checks into Python assertions in Stage 3.")


def show_automation():
    st.header("🐍 Stage 3 — API Automation from Zero")
    st.markdown("**Goal:** Write and run your first automated API test. Start from the manual test case you already understand.")
    st.subheader("Step 1 · What is automation?")
    st.markdown("""
Manual testing: you click **Send**, inspect the response, and decide PASS/FAIL.
Automation: **Python** sends the request; **requests** handles HTTP; **assert** checks actual vs expected; **pytest** runs tests and reports results.

A test should contain **Arrange → Act → Assert**:
1. **Arrange:** choose URL and expected status.
2. **Act:** call the API.
3. **Assert:** compare status and JSON with expected values.
""")
    st.subheader("Step 2 · Learn the four essential Python lines")
    st.code('''import requests  # HTTP library
response = requests.get("https://dummyjson.com/products/1", timeout=10)
assert response.status_code == 200
assert response.json()["id"] == 1''', language="python")
    st.markdown("""
- `import requests` loads the HTTP client library.
- `requests.get(...)` sends GET to the server. `timeout=10` avoids hanging forever.
- `response.status_code` reads the HTTP status.
- `response.json()` parses the response JSON into Python data.
- `assert` fails the test if its condition is false.
""")
    st.subheader("Step 3 · Build your own pytest test interactively")
    choice = st.selectbox("Choose manual test to automate", [c["id"]+" — "+c["title"] for c in CASES], key="automation_case")
    case = CASES[[c["id"] for c in CASES].index(choice.split(" — ")[0])]
    name = st.text_input("Python test function name", value="test_"+case["title"].lower().replace(" ","_"), key="automation_name")
    try:
        code = generate_test(case, name)
    except ValueError as exc:
        st.error(str(exc))
        return
    st.code(code, language="python")
    st.download_button("↓ Download runnable pytest file", code, "test_my_api.py", "text/x-python", key="automation_export")
    st.subheader("Step 4 · Run the same check live")
    st.caption("This button executes a controlled Python request and assertions equivalent to the generated test; it does not execute arbitrary user Python code.")
    if st.button("▶ Run my automated assertions", type="primary", key="automation_run"):
        try:
            response = requests.get(BASE+case["path"], timeout=10)
            checks, payload = evaluate(response, case)
            st.session_state.auto_result = {"case":case["id"],"checks":checks,"actual":response.status_code}
        except requests.RequestException as exc:
            st.session_state.auto_result = {"case":case["id"],"error":str(exc)}
    result = st.session_state.get("auto_result")
    if result and result["case"] == case["id"]:
        if "error" in result:
            st.error("Request error: "+result["error"])
        else:
            for label, passed in result["checks"].items():
                (st.success if passed else st.error)(f"{'PASS' if passed else 'FAIL'} — {label}")
            st.markdown("**pytest equivalent:** " + ("1 passed" if all(result["checks"].values()) else "1 failed"))
    st.subheader("Step 5 · Run your downloaded test in VS Code")
    st.markdown("Install **Python 3.11+**, **VS Code**, and Microsoft's **Python** extension. Open a new folder in VS Code, save the downloaded file there, then open **Terminal → New Terminal**.")
    st.code(r"""py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install requests pytest
python -m pytest -v test_my_api.py""", language="powershell")
    st.caption("Windows PowerShell shown. If activation is blocked, use .venv\\Scripts\\python.exe -m pip install requests pytest and .venv\\Scripts\\python.exe -m pytest -v test_my_api.py.")
    st.markdown("**Read the output:** PASSED means all assertions matched; FAILED means at least one did not. For a failing test, pytest shows the assertion and traceback.")
    st.subheader("Step 6 · Grow your automation framework")
    st.markdown("""
After your first test passes:
1. Add a second test for the missing-product **404** case.
2. Use `@pytest.mark.parametrize` to run multiple IDs.
3. Create a `requests.Session()` fixture for shared headers and configuration.
4. Separate API client code from tests when your suite grows.
5. Add tests for POST/PUT/PATCH/DELETE, authentication, invalid input, and response schema.
6. Run tests from VS Code or a CI pipeline.

The repository includes a ready-to-run **local_automation/** folder with fixtures and multiple sample tests. No Streamlit or OpenAI key is needed to run them.
""")
    st.info("DummyJSON write operations are simulated and do not persist changes. Only use dummy credentials for training.")


def show_course_path():
    st.title("🎓 API QA Academy — Beginner Learning Path")
    st.markdown("Follow these three stages in order. Every stage uses the same shopping-product API, so each new concept builds on the previous one.")
    foundation, manual, automation = st.tabs([
        "1️⃣ API Foundations", "2️⃣ Manual API Testing", "3️⃣ API Automation"
    ])
    with foundation:
        show_foundations()
    with manual:
        show_manual()
    with automation:
        show_automation()
