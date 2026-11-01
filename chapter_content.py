"""Chapter-specific teaching material for all 36 API QA Academy modules."""
import streamlit as st

FOUNDATION = {
"01": ("What is an API?", "A shopping app asks another system for a product. The API is the contract: which requests are accepted and what comes back.", "GET /products/1", "Name the client, API server, business logic, and data source.", "API is the communication contract; the server implements it."),
"02": ("Client, server and endpoint", "A client initiates a request. The API server receives it, routes it to the matching handler, and returns a response. An endpoint is a method plus a URL path.", "GET /users/1", "Explain which system is the client and which system processes the request.", "An endpoint identifies a specific operation on a resource."),
"03": ("Request and response", "A request contains a method, target, headers and sometimes a body. A response contains status, headers and often JSON.", "GET /products/1", "Identify method, path, request header, response status and response body.", "Request goes to the server; response comes back."),
"04": ("HTTP methods", "GET retrieves; POST commonly creates; PUT replaces or updates as specified; PATCH partially updates; DELETE removes. The API contract determines exact behavior.", "POST /products/add", "Choose the correct method for reading, creating, updating and deleting.", "Method communicates the intended action."),
"05": ("HTTP status codes", "2xx success, 4xx client-side errors, 5xx server-side errors. QA must assert the status documented for the scenario.", "GET /products/999999", "Explain why an expected 404 can be a passing negative test.", "Expected and actual status must match."),
"06": ("JSON basics", "JSON objects use key/value pairs; arrays hold ordered values. Strings use double quotes, numbers are unquoted, booleans are true/false, and null means no value.", 'JSON: {"id":1,"tags":["qa"],"active":true}', "Identify the types of id, tags and active and validate a JSON example.", "JSON carries structured data, not the HTTP status."),
"07": ("HTTP headers", "Headers are metadata such as Accept, Content-Type and Authorization. Accept describes the preferred response type; Content-Type describes the body being sent.", "Accept: application/json", "Compare Accept and Content-Type, then explain an Authorization bearer token.", "Headers are separate from the JSON body."),
"08": ("Path versus query parameters", "A path parameter identifies a resource such as /users/1. A query parameter modifies retrieval such as /users?limit=5.", "GET /users?limit=5&skip=0", "Identify path and query parameters and design pagination checks.", "Path often selects a resource; query refines the request."),
"09": ("Authentication concepts", "Authentication proves identity; authorization determines allowed actions. A login may return an access token used in the Authorization header.", "POST /auth/login → Bearer token", "Compare missing, invalid and valid credentials and token scenarios.", "Being logged in does not mean access to every resource."),
}
MANUAL = {
"10": ("GET happy path", "Send GET /products/1, expect 200, check JSON id and required fields."),
"11": ("POST request", "Send a JSON body to /users/add; validate returned fields and the API-documented status. DummyJSON does not persist writes."),
"12": ("Manual PUT and PATCH", "Manually send PUT and PATCH to /users/2 with JSON bodies. Compare the returned ID, changed fields, status, and documented behavior. DummyJSON writes are simulated."),
"13": ("Manual DELETE", "Manually send DELETE /users/1, record the HTTP status, verify id and isDeleted/deletedOn response fields, and note that DummyJSON does not persist the deletion."),
"14": ("JSON response validation", "Inspect /posts/1; verify keys, values, nested data, required fields and types."),
"15": ("Authentication testing", "Use sample login, inspect access token, test /auth/me with valid and invalid tokens."),
"16": ("Test-case design", "Write test ID, preconditions, request, steps, expected response, actual response and PASS/FAIL."),
}
AUTOMATION = {
"17": ("Python requests", "Import requests, call requests.get with timeout, inspect response.status_code and response.json()."),
"18": ("GET assertions", "Use assert for status, important JSON keys, values and types."),
"19": ("Status assertions", "Assert exact documented status; include a negative test expecting 404."),
"20": ("JSON assertions", "Parse response.json once, assert nested fields, list types and required values."),
"21": ("POST automation", "Send json=payload; assert the API-documented status and echoed fields."),
"22": ("PUT/PATCH automation", "Send a patch payload and assert updated fields without assuming persistence."),
"23": ("DELETE automation", "Send DELETE and assert documented response fields such as isDeleted."),
"24": ("Headers in Python", "Use headers={...}; inspect response.headers and validate content type."),
"25": ("Query parameters", "Use params={'limit': 5, 'skip': 5}; assert pagination metadata and item count."),
"26": ("Login automation", "POST sample credentials; assert success and capture accessToken without printing real secrets."),
"27": ("Bearer token automation", "Use Authorization: Bearer token to call /auth/me and validate identity."),
"28": ("Negative automation", "Assert expected errors for missing resources and invalid inputs."),
"29": ("pytest basics", "Name files test_*.py and functions test_*; run python -m pytest -v."),
"30": ("pytest fixtures", "Use @pytest.fixture to share a requests.Session or base URL across tests."),
"31": ("Parametrization", "Use @pytest.mark.parametrize to run one test against multiple IDs."),
"32": ("Reusable API clients", "Move requests into helper functions and keep assertions in tests."),
"33": ("Timeout and error handling", "Set request timeouts and make network failures clear in test reports."),
"34": ("Test data", "Separate test payloads from test logic; use fixtures and avoid real secrets."),
"35": ("Framework structure", "Organize tests/, clients/, data/, conftest.py and pytest.ini."),
"36": ("Final project", "Combine positive/negative tests, auth, CRUD simulations, fixtures, parametrization and reports."),
}

def chapter_material(module):
    mid = module["id"]
    if mid in FOUNDATION:
        title, explanation, example, task, takeaway = FOUNDATION[mid]
        return title, explanation, example, task, takeaway
    if mid in MANUAL:
        title, explanation = MANUAL[mid]
        return title, explanation, f"{module['method']} {module['path']}", module["assignment"], "Always compare actual results with a documented expected result."
    title, explanation = AUTOMATION[mid]
    return title, explanation, f"{module['method']} {module['path']}", module["assignment"], "Automated tests must contain meaningful assertions."

def chapter_quiz(module):
    mid = module["id"]
    if mid in FOUNDATION:
        questions = {
            "01": ("What is an API?", ["A communication contract between software", "Only a database", "Only a webpage"], 0),
            "02": ("Who initiates an API request?", ["Database", "Client", "JSON"], 1),
            "03": ("What does an HTTP response contain?", ["Only a URL", "Only Python", "Status, headers and possibly body"], 2),
            "04": ("Which method usually retrieves a resource?", ["GET", "DELETE", "PATCH"], 0),
            "05": ("Can an expected 404 be a passing test?", ["No", "Yes", "Only with POST"], 1),
            "06": ("Which is valid JSON?", ["{'id':1}", '{"id":1}', "{id:1}"], 1),
            "07": ("Which header describes the request body's format?", ["Accept", "Host", "Content-Type"], 2),
            "08": ("Which is a query parameter?", ["/users/1", "?limit=5", "GET"], 1),
            "09": ("What does authorization decide?", ["Which actions a caller may perform", "Which HTTP method exists", "Whether JSON uses braces"], 0),
        }
        return questions[mid]
    other = {
        "10": ("For a GET happy-path test, what should QA validate?", ["Only response time", "Status and product data", "Only URL length"], 1),
        "11": ("What is sent in a JSON POST request?", ["A payload in the body", "Only a status code", "Only a response header"], 0),
        "12": ("Which method usually changes only selected fields?", ["PATCH", "GET", "DELETE"], 0),
        "13": ("What should a manual DELETE test verify?", ["Documented status and deletion indicators", "Only page color", "Only request size"], 0),
        "14": ("Which JSON check is useful?", ["Required field and data type", "Number of spaces", "URL font"], 0),
        "15": ("What should a protected endpoint reject?", ["Valid authorized token", "Missing or invalid token", "Valid JSON"], 1),
        "16": ("What belongs in a manual test case?", ["Only test title", "Steps and expected result", "Only screenshots"], 1),
        "17": ("Which Python library sends HTTP requests?", ["requests", "math", "random"], 0),
        "18": ("Which statement validates an HTTP result?", ["print(response)", "assert response.status_code == 200", "pass"], 1),
        "19": ("Which status assertion is best for a documented 404?", ["assert status == 404", "assert status == 200", "print(status)"], 0),
        "20": ("How do you parse JSON with requests?", ["response.json()", "response.path()", "response.headers()"], 0),
        "21": ("How do you send JSON with requests.post?", ["json=payload", "print=payload", "status=payload"], 0),
        "22": ("Which Python call sends a PATCH?", ["requests.get", "requests.patch", "requests.options"], 1),
        "23": ("What can DummyJSON DELETE return?", ["Deletion indicators", "A persistent deletion guarantee", "A Python fixture"], 0),
        "24": ("Where do request headers go in requests.get?", ["headers={...}", "assert={...}", "pytest={...}"], 0),
        "25": ("How should query parameters be passed?", ["params={...}", "body_status=200", "print(...)"], 0),
        "26": ("What should you capture after successful login?", ["accessToken", "Server IP", "Screenshot only"], 0),
        "27": ("What does Bearer authentication require?", ["Authorization header with token", "JSON string only", "A 404 response"], 0),
        "28": ("When does a negative test pass?", ["When documented error matches actual", "Only on 200", "Whenever response is long"], 0),
        "29": ("Which test function is discovered by pytest?", ["def test_get_user():", "def run_user():", "def helper():"] , 0),
        "30": ("What is a pytest fixture?", ["Reusable setup", "HTTP status", "JSON key"], 0),
        "31": ("What does parametrization enable?", ["One test with multiple inputs", "No assertions", "Only one request"], 0),
        "32": ("What should reusable API client helpers handle?", ["Sending requests", "Choosing test PASS without assertions", "Changing production data always"], 0),
        "33": ("Why specify timeout=10?", ["Avoid indefinitely waiting", "Force 200 status", "Remove headers"], 0),
        "34": ("Where should reusable test data live?", ["Separate fixtures/data when useful", "In public secrets", "Only screenshots"], 0),
        "35": ("What belongs in a maintainable test framework?", ["Clients, tests, fixtures and config", "One huge print statement", "Only screenshots"], 0),
        "36": ("What does a final API suite need?", ["Positive/negative checks and reusable automation", "Only GET 200", "No assertions"], 0),
    }
    return other[mid]

def show_chapter(module):
    title, explanation, example, task, takeaway = chapter_material(module)
    st.subheader(f"Chapter {module['id']} · {title}")
    st.markdown(explanation)
    if module["id"] in {"01", "02", "03"}:
        st.graphviz_chart("""
        digraph {
          rankdir=LR;
          node [shape=box style="rounded,filled" fillcolor="#e0f2fe" color="#0284c7"];
          Client [label="Client / UI"];
          API [label="API server"];
          Data [label="Data / Service"];
          Client -> API [label="HTTP request"];
          API -> Data [label="Business logic"];
          Data -> API [label="Result"];
          API -> Client [label="HTTP response"];
        }
        """, use_container_width=True)
    elif module["stage"] == "Manual API Testing":
        st.graphviz_chart("""
        digraph {
          rankdir=LR;
          node [shape=box style="rounded,filled" fillcolor="#dcfce7"];
          A [label="Requirement"]; B [label="Test case"]; C [label="Send request"];
          D [label="Compare expected vs actual"]; E [label="PASS / FAIL"];
          A -> B -> C -> D -> E;
        }
        """, use_container_width=True)
    elif module["stage"] in {"API Automation", "Advanced Automation"}:
        st.graphviz_chart("""
        digraph {
          rankdir=LR;
          node [shape=box style="rounded,filled" fillcolor="#fef3c7"];
          A [label="pytest test"]; B [label="requests HTTP call"];
          C [label="API response"]; D [label="assertions"]; E [label="PASS / FAIL"];
          A -> B -> C -> D -> E;
        }
        """, use_container_width=True)
    st.markdown("**Chapter example**")
    st.code(example, language="text")
    st.info(f"**Your chapter exercise:** {task}")
    st.caption(f"Key takeaway: {takeaway}")
    if mid_is_foundations(module) and module["id"] == "06":
        import json
        raw = st.text_area("Edit and validate JSON", '{"id":1,"active":true,"tags":["api"]}', key="chapter_json_06")
        if st.button("Validate JSON", key="chapter_validate_06"):
            try:
                st.json(json.loads(raw))
                st.success("Valid JSON")
            except ValueError as exc:
                st.error(f"Invalid JSON: {exc}")
    if module["id"] == "07":
        header = st.selectbox("Choose header to inspect", ["Accept", "Content-Type", "Authorization"], key="chapter_header_07")
        descriptions = {
            "Accept": "Preferred response media type, such as application/json.",
            "Content-Type": "Format of the request body, such as application/json.",
            "Authorization": "Credentials for protected resources, often Bearer <token>.",
        }
        st.info(descriptions[header])
    if module["id"] == "08":
        limit = st.slider("Requested number of users", 1, 10, 5, key="chapter_limit_08")
        st.code(f"GET /users?limit={limit}&skip=0", language="http")
    st.markdown("#### Knowledge check for this chapter")
    q, options, correct = chapter_quiz(module)
    choice = st.radio(q, options, key=f"chapter_quiz_{module['id']}")
    if st.button("Check chapter answer", key=f"chapter_check_{module['id']}"):
        if choice == options[correct]:
            st.success("Correct! You understood this chapter.")
        else:
            st.warning(f"Review the explanation. Hint: {takeaway}")

def mid_is_foundations(module):
    return module["stage"] == "API Foundations"
