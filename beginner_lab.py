"""Interactive beginner lab: conceptual API flow, real request checks, and pytest export."""
import json
import re
import streamlit as st
import requests

BASE = "https://dummyjson.com"
SCENARIOS = {
    "Existing product": {"path": "/products/1", "status": 200, "field": "id", "expected": 1},
    "Missing product": {"path": "/products/999999", "status": 404, "field": None, "expected": None},
    "Product search": {"path": "/products/search?q=phone", "status": 200, "field": "products", "expected": "list"},
}


def build_pytest(path, status, field=None, expected=None):
    """Generate executable pytest with no Streamlit dependency."""
    if not re.fullmatch(r"/products(?:/[0-9]+|/search\?q=[A-Za-z0-9_-]+)?", path):
        raise ValueError("Choose a supported products endpoint.")
    assertions = [f"    assert response.status_code == {status}, response.text"]
    if field:
        assertions.append("    data = response.json()")
        if expected == "list":
            assertions.append(f"    assert isinstance(data[{field!r}], list)")
        else:
            assertions.append(f"    assert data[{field!r}] == {expected!r}")
    return (
        "import requests\n\n"
        "def test_product_api():\n"
        f"    response = requests.get({(BASE + path)!r}, timeout=10)\n"
        + "\n".join(assertions) + "\n"
    )


def show_beginner_lab():
    st.header("🧭 Start Here: API to QA Automation")
    st.info("Start with the picture, then make a test case, run it, and export the exact test for VS Code.")
    st.subheader("1 · What happens when two applications communicate?")
    st.markdown(
        "**Example:** A shopping app needs product information. It does not read the store database directly. "
        "It sends an HTTP request to an API. The server checks the request, obtains data, and returns an HTTP response."
    )
    st.graphviz_chart("""
    digraph API {
      rankdir=LR;
      node [shape=box style="rounded,filled" fillcolor="#e0f2fe" color="#0369a1" fontname="Arial"];
      Client [label="Shopping App / QA Tester"];
      API [label="HTTP API\nGET /products/1"];
      Logic [label="Server / Business Rules"];
      Data [label="Product Data"];
      Client -> API [label="1. Request"];
      API -> Logic [label="2. Validate"];
      Logic -> Data [label="3. Read"];
      Data -> Logic [label="4. Product"];
      Logic -> API [label="5. JSON + status"];
      API -> Client [label="6. Response"];
    }
    """, use_container_width=True)
    with st.expander("Explain each part in plain English", expanded=True):
        st.markdown(
            "**Client:** the app or tester asking a question.  \n"
            "**Endpoint:** the URL path that identifies the resource.  \n"
            "**Method:** GET reads, POST creates, PUT/PATCH updates, DELETE removes.  \n"
            "**Headers:** extra information such as Accept or Authorization.  \n"
            "**Body:** data sent with some requests, often JSON.  \n"
            "**Response:** status code, headers, and often JSON.  \n"
            "**QA's job:** compare actual response with documented expected behavior, including errors."
        )
    st.subheader("1A · What exactly is an API server?")
    st.markdown("""
An **API (Application Programming Interface)** is a set of rules and endpoints that let software systems communicate.
An **API server** is a running application that listens for HTTP requests, decides what the caller is allowed to do,
runs business rules, may read or write a database, and sends an HTTP response.

**Important distinction:** the API is the *interface/contract*; the API server is the *software handling the calls*.
A server can be a cloud service, a container, or a program running on a laptop. The API server is not necessarily the database.
""")
    with st.expander("Example: what happens when you click View Product?", expanded=True):
        st.markdown("""
1. **User interface:** You click a product in the shopping app.
2. **Client:** The browser/mobile app sends `GET https://dummyjson.com/products/1`.
3. **Internet:** DNS resolves the hostname; HTTPS protects data in transit.
4. **API server:** A web server receives the request and routes `GET /products/1` to the appropriate handler.
5. **Business logic:** The handler validates inputs and checks any required permissions.
6. **Data layer:** It obtains product information from storage or another service.
7. **Response:** The server returns a status (such as 200), headers, and a JSON body.
8. **UI:** The app reads the JSON and displays a product title and price.
9. **QA:** We verify status, JSON schema/values, error behavior, permissions, and response time.
""")
    st.subheader("1B · Explore the HTTP request and response")
    st.code("GET /products/1 HTTP/1.1\\nHost: dummyjson.com\\nAccept: application/json", language="http")
    st.markdown("**Request breakdown:** `GET` is the method; `/products/1` is the endpoint path; `Host` identifies the server; `Accept` requests JSON.")
    st.code('HTTP/1.1 200 OK\\nContent-Type: application/json\\n\\n{"id":1,"title":"Example product"}', language="http")
    st.caption("The response above is illustrative, not the exact live DummyJSON product.")
    st.markdown("**Response breakdown:** `200` is the HTTP status; `Content-Type` describes the response format; the JSON body carries data.")
    st.subheader("1C · Who does what? Client vs API server vs database")
    st.table([
        {"Component": "Client (browser/mobile app)", "Responsibility": "Displays UI and sends HTTP requests", "QA example": "Does clicking View Product send the right request?"},
        {"Component": "API server", "Responsibility": "Routes requests, validates input, enforces permissions, returns responses", "QA example": "Is an invalid ID rejected with the expected error?"},
        {"Component": "Database / data service", "Responsibility": "Stores or supplies product information", "QA example": "Is the correct product returned without exposing private fields?"},
        {"Component": "QA automation", "Responsibility": "Sends requests and asserts expected behavior", "QA example": "Does status equal 200 and JSON id equal 1?"},
    ])
    st.subheader("1D · Choose an API method to see what changes")
    method_explanations = {
        "GET": ("Read an existing product", "GET /products/1", "Usually no request body; expect data or a documented error."),
        "POST": ("Ask server to create a product", "POST /products/add", 'JSON body: {"title":"QA Demo"}; validate returned fields and creation status.'),
        "PUT": ("Replace or update a resource according to the API contract", "PUT /products/1", "Send a JSON body; check which fields change."),
        "PATCH": ("Partially update a resource", "PATCH /products/1", "Send only the field to change; check unrelated fields remain as expected."),
        "DELETE": ("Ask server to delete a resource", "DELETE /products/1", "Verify documented deletion response and permissions."),
    }
    chosen_method = st.selectbox("HTTP method", list(method_explanations), key="starter_method_explainer")
    purpose, example, qa_note = method_explanations[chosen_method]
    st.markdown(f"**Purpose:** {purpose}")
    st.code(example, language="http")
    st.info(f"**QA validation:** {qa_note}")
    st.caption("DummyJSON write operations are simulated and do not persist changes.")
    st.subheader("1E · What can go wrong? Think like a QA engineer")
    st.markdown("""
- **200 OK:** Request succeeded; still check the JSON is correct.
- **201 Created:** Resource created, if the API contract specifies this.
- **400 Bad Request:** Invalid request; check the error message and validation rules.
- **401 Unauthorized:** Authentication is missing or invalid.
- **403 Forbidden:** The caller is authenticated but lacks permission.
- **404 Not Found:** The resource does not exist.
- **500 Internal Server Error:** Server failed; log a defect if unexpected.

**Practical QA rule:** An expected 404 can be a **passing negative test**.
The correct expectation comes from the API specification, not from assuming every API must return 200.
""")
    st.subheader("2 · Choose a scenario and write your test case")
    scenario = st.selectbox("Business situation", list(SCENARIOS), key="starter_scenario")
    s = SCENARIOS[scenario]
    st.code(f"GET {BASE}{s['path']}", language="http")
    requirement = st.text_input("Requirement / purpose", value=f"Verify {scenario.lower()} returns the expected API response", key=f"req_{scenario}")
    st.markdown(f"**Expected HTTP status:** `{s['status']}`")
    if s["field"]:
        st.markdown(f"**Expected JSON check:** `{s['field']}` = `{s['expected']}`")
    st.markdown("**Test steps:** (1) Send GET request; (2) capture status and JSON; (3) compare expected and actual; (4) record PASS/FAIL.")
    if st.button("▶ Run real API test", type="primary", key="starter_run"):
        try:
            response = requests.get(BASE + s["path"], timeout=10)
            payload = response.json()
            checks = {"HTTP status": response.status_code == s["status"]}
            if s["field"]:
                value = payload.get(s["field"]) if isinstance(payload, dict) else None
                checks[f"JSON {s['field']}"] = isinstance(value, list) if s["expected"] == "list" else value == s["expected"]
            st.session_state.starter_result = {
                "scenario": scenario, "status": response.status_code, "checks": checks, "body": payload,
            }
        except (requests.RequestException, ValueError) as exc:
            st.session_state.starter_result = {"scenario": scenario, "error": str(exc)}
    result = st.session_state.get("starter_result")
    if result and result["scenario"] == scenario:
        if "error" in result:
            st.error(f"Network or response error: {result['error']}")
        else:
            for name, passed in result["checks"].items():
                (st.success if passed else st.error)(f"{'PASS' if passed else 'FAIL'} — {name}")
            st.caption(f"Actual status: {result['status']} · Requirement: {requirement}")
            with st.expander("Actual JSON response"):
                st.json(result["body"])
    st.subheader("3 · Turn the same manual test into automation")
    st.markdown("An **assertion** makes Python decide whether the actual result matches the expected result. "
                "pytest discovers functions starting with `test_` and reports PASS or FAIL.")
    code = build_pytest(**s)
    st.code(code, language="python")
    st.download_button("↓ Download test_product_api.py", code, "test_product_api.py", "text/x-python", key="starter_download")
    st.subheader("4 · Run it in VS Code (without Streamlit)")
    st.code("py -m venv .venv\n.venv\\Scripts\\activate\npython -m pip install requests pytest\npython -m pytest -v test_product_api.py", language="powershell")
    st.caption("Windows commands above. For macOS/Linux: python3 -m venv .venv; source .venv/bin/activate; python -m pip install requests pytest.")
    st.markdown("Open **README.md → VS Code local automation guide** for installation, project structure, debugging, "
                "adding your own test cases, and troubleshooting.")
    st.subheader("5 · Challenge")
    st.markdown("Try the missing-product scenario. Why should a **404** be a PASS? "
                "Because QA checks whether the API behaves **as expected**, not whether every response is 200.")
    choice = st.radio("A missing product returns 404. What should your test report?", ["FAIL: status is not 200", "PASS: expected 404 matches actual 404"], key="starter_quiz")
    if st.button("Check my reasoning", key="starter_quiz_check"):
        if choice.startswith("PASS"):
            st.success("Correct! A negative test passes when the error behavior matches the requirement.")
        else:
            st.warning("Negative tests intentionally send invalid input. Expected 404 can be a passing test.")
