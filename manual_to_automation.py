"""Manual-to-automation walkthrough shown in every API Automation lesson.

All requests are opt-in. DummyJSON simulates writes; no changes persist.
"""
import json
import streamlit as st

from assignment_help import solution_for

BASE = "https://dummyjson.com"

CASES = {
    "17": ("Read a user profile", "GET", "/users/1", None, 200, ["HTTP 200", "JSON contains firstName", "Print status and firstName"]),
    "18": ("Validate a user profile", "GET", "/users/2", None, 200, ["HTTP 200", "id equals 2", "firstName is a nonempty string", "firstName has type str"]),
    "19": ("Confirm an existing user", "GET", "/users/1", None, 200, ["Exact HTTP 200, not just any 2xx"]),
    "20": ("Validate a post JSON contract", "GET", "/posts/1", None, 200, ["HTTP 200", "id equals 1", "title is a nonempty string", "userId is an integer"]),
    "21": ("Create a user (simulated)", "POST", "/users/add", {"firstName": "Alex", "age": 30}, 201, ["HTTP 201", "Response has an integer id", "Returned firstName and age match request", "Creation is simulated, not persisted"]),
    "22": ("Update a user (simulated)", "PATCH", "/users/2", {"lastName": "QA"}, 200, ["HTTP 200", "User id remains 2", "lastName equals QA", "Update is simulated, not persisted"]),
    "23": ("Delete a user (simulated)", "DELETE", "/users/1", None, 200, ["HTTP 200", "id equals 1", "isDeleted is true", "deletedOn is present", "Deletion is simulated, not persisted"]),
    "24": ("Inspect response headers", "GET", "/test", None, 200, ["HTTP 200", "Content-Type includes application/json"]),
    "25": ("Test pagination", "GET", "/users?limit=5&skip=5", None, 200, ["HTTP 200", "limit equals 5", "skip equals 5", "users list contains at most 5 items"]),
    "26": ("Login with public demo credentials", "POST", "/auth/login", {"username": "emilys", "password": "emilyspass"}, 200, ["HTTP 200", "accessToken is present", "Never log or expose real tokens"]),
    "27": ("Request a protected resource with an invalid token", "GET", "/auth/me", None, 401, ["HTTP 401 or 403 for invalid bearer token", "Valid-token scenario requires login first"]),
    "28": ("Request a missing user", "GET", "/users/999999", None, 404, ["Exact HTTP 404", "Error body describes missing resource"]),
}

def _evaluate(module_id, status, data, headers):
    if module_id == "27":
        return [("Invalid bearer token is rejected", status in (401, 403))]
    expected = CASES[module_id][4]
    checks = [(f"HTTP status is {expected}", status == expected)]
    if not isinstance(data, dict):
        return checks + [("JSON object returned", False)]
    if module_id in ("17", "18"):
        checks += [("User ID matches request", data.get("id") == (2 if module_id == "18" else 1)),
                   ("firstName is nonempty text", isinstance(data.get("firstName"), str) and bool(data.get("firstName", "").strip()))]
    elif module_id == "19":
        checks.append(("User ID is 1", data.get("id") == 1))
    elif module_id == "20":
        checks += [("Post ID is 1", data.get("id") == 1),
                   ("title is nonempty text", isinstance(data.get("title"), str) and bool(data.get("title", "").strip())),
                   ("userId is integer", type(data.get("userId")) is int)]
    elif module_id == "21":
        checks += [("New ID is integer", type(data.get("id")) is int),
                   ("Returned values match request", data.get("firstName") == "Alex" and data.get("age") == 30)]
    elif module_id == "22":
        checks += [("ID remains 2", data.get("id") == 2), ("lastName updated", data.get("lastName") == "QA")]
    elif module_id == "23":
        checks += [("ID is 1", data.get("id") == 1), ("isDeleted is true", data.get("isDeleted") is True),
                   ("deletedOn is present", bool(data.get("deletedOn")))]
    elif module_id == "24":
        checks.append(("Content-Type includes application/json", "application/json" in headers.get("Content-Type", "").lower()))
    elif module_id == "25":
        checks += [("limit is 5", data.get("limit") == 5), ("skip is 5", data.get("skip") == 5),
                   ("users has at most five records", isinstance(data.get("users"), list) and len(data["users"]) <= 5)]
    elif module_id == "26":
        checks.append(("Access token exists", bool(data.get("accessToken"))))
    elif module_id == "28":
        checks.append(("Error information returned", bool(data.get("message"))))
    return checks


def show_manual_to_automation(module, send_api):
    mid = module["id"]
    if mid not in CASES:
        return
    title, method, path, body, expected, checks = CASES[mid]
    st.markdown("### From manual API testing to automation")
    st.markdown("**Use case:** " + title)
    st.graphviz_chart("""
    digraph {
      rankdir=LR;
      node [shape=box style="rounded,filled" fillcolor="#e0f2fe"];
      Manual [label="1. Manually send HTTP request"];
      Observe [label="2. Inspect response"];
      Test [label="3. Write Python test"];
      Assert [label="4. Assert expected result"];
      Manual -> Observe -> Test -> Assert;
    }
    """, use_container_width=True)
    st.markdown("**Step 1 — Send the request manually**")
    st.code(f"{method} {BASE}{path}", language="http")
    if body is not None:
        st.caption("JSON request body")
        st.code(json.dumps(body, indent=2), language="json")
    if mid == "27":
        st.caption("For this negative test, the request includes Authorization: Bearer invalid-token.")
    st.markdown("**Step 2 — Predict the expected response before sending**")
    st.write(f"Expected status: **{expected}**" if mid != "27" else "Expected status: **401 or 403** (unauthorized/forbidden)")
    for check in checks:
        st.markdown("- " + check)
    if st.button("Send this example API request", key=f"walkthrough_send_{mid}"):
        try:
            request_headers = {"Accept": "application/json"}
            if mid == "27":
                request_headers["Authorization"] = "Bearer invalid-token"
            response, data, elapsed = send_api(method, path, request_headers, body)
            # Never show authentication credentials or returned access tokens.
            safe_data = dict(data) if isinstance(data, dict) else data
            if mid == "26" and isinstance(safe_data, dict):
                safe_data = {k: ("[REDACTED]" if "token" in k.lower() else v) for k, v in safe_data.items()}
            st.session_state[f"walkthrough_result_{mid}"] = {
                "status": response.status_code, "data": safe_data,
                "headers": dict(response.headers), "elapsed": elapsed,
                "checks": _evaluate(mid, response.status_code, data, response.headers),
            }
        except Exception as exc:
            st.error(f"Request could not complete: {type(exc).__name__}: {exc}")
    result = st.session_state.get(f"walkthrough_result_{mid}")
    if result:
        st.markdown("**Actual response**")
        st.write(f"HTTP **{result['status']}** · {result['elapsed']} ms")
        st.json(result["data"])
        st.markdown("**Manual QA comparison — expected vs actual**")
        for name, passed in result["checks"]:
            st.write(("✅ PASS — " if passed else "❌ FAIL — ") + name)
        if all(passed for _, passed in result["checks"]):
            st.success("All checks passed for this response. This does not prove every scenario works.")
        else:
            st.warning("At least one check failed. Record the expected and actual values.")
    st.markdown("**Step 3 — Automate the same checks**")
    st.markdown("In Python, `requests` sends the HTTP request; `assert` turns each manual observation into a repeatable PASS/FAIL check.")
    st.code(solution_for(mid), language="python")
    st.markdown("**Step 4 — What automation coverage is needed?**")
    st.markdown("For this use case, include the checks above plus negative or boundary scenarios where relevant. Keep each independent behavior in a separate test when practical.")
    if mid in ("19", "27", "28"):
        st.info("This reference includes multiple positive/negative tests. Run all of them, not just the one manual example.")
    if mid in ("21", "22", "23"):
        st.warning("DummyJSON write operations are simulated. Do not write a follow-up persistence assertion expecting saved changes.")
    st.caption("Run this chapter's example in the Practice tab; for a real pytest suite, use VS Code and python -m pytest -v.")
