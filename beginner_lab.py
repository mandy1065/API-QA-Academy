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
