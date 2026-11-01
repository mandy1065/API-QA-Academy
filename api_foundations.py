"""Foundations-first interactive API course for people new to HTTP."""
import json
import streamlit as st


def show_foundations():
    st.header("📘 API Foundations — Start from Zero")
    st.markdown("**No programming knowledge needed.** Follow the same shopping-app example from the screen to the API and back.")
    st.subheader("Lesson 1 · What is an API?")
    st.markdown("""
**API** stands for **Application Programming Interface**. It is a documented way for one program to ask another program for information or to perform an action.

Imagine a shopping app. When you tap a product, the app needs its name and price. Instead of directly opening the store's database, it calls an API endpoint. The API server processes the request and sends data back.

**Everyday analogy:** You (the customer) tell a waiter (the API) what you want. The waiter passes the order to the kitchen (server/business logic), then brings back the meal (response). The menu is like the API documentation: it tells you what you can request.
""")
    st.graphviz_chart("""
    digraph {
      rankdir=LR;
      node [shape=box style="rounded,filled" color="#2563eb" fillcolor="#eff6ff"];
      A [label="Shopping app\nCLIENT"];
      B [label="GET /products/1\nAPI ENDPOINT"];
      C [label="API server\nRULES + LOGIC"];
      D [label="Product data"];
      A -> B [label="HTTP request"];
      B -> C;
      C -> D [label="Read"];
      D -> C [label="Product"];
      C -> A [label="HTTP response\n200 + JSON"];
    }
    """, use_container_width=True)
    st.markdown("**API vs API server:** The API is the *interface/contract*; the API server is the *running software* that implements it. The database is a separate place where information may be stored.")

    st.subheader("Lesson 2 · Anatomy of a URL and endpoint")
    st.code("https://dummyjson.com/products/1", language="text")
    st.table([
        {"Part": "https://", "Meaning": "Protocol: secure HTTP communication"},
        {"Part": "dummyjson.com", "Meaning": "Host: which server to contact"},
        {"Part": "/products", "Meaning": "Resource path: products"},
        {"Part": "/1", "Meaning": "Path parameter: product ID 1"},
        {"Part": "?limit=5", "Meaning": "Optional query parameter: request five items"},
    ])
    st.markdown("An **endpoint** combines an HTTP method and URL path, such as `GET /products/1`. The same path can behave differently with a different method.")

    st.subheader("Lesson 3 · What is an HTTP request?")
    st.markdown("A **request** is the message the client sends to an API server. It has a method, URL, headers, and sometimes a body.")
    st.code("GET /products/1 HTTP/1.1\nHost: dummyjson.com\nAccept: application/json", language="http")
    st.markdown("""
- **Method:** `GET` means retrieve information.
- **URL/path:** `/products/1` identifies the product.
- **Request headers:** metadata that tells the server how to handle the request.
- **Request body:** data sent *to* the server, often with POST, PUT or PATCH. This GET example does not need a body.
""")

    st.subheader("Lesson 4 · Headers explained")
    st.markdown("Headers are **key: value** pairs, separate from the JSON body. They carry instructions or metadata.")
    st.table([
        {"Header": "Accept: application/json", "Purpose": "Client prefers a JSON response"},
        {"Header": "Content-Type: application/json", "Purpose": "The request body is JSON"},
        {"Header": "Authorization: Bearer TOKEN", "Purpose": "Supplies an access token for protected endpoints"},
        {"Header": "User-Agent: MyApp/1.0", "Purpose": "Identifies the client software"},
    ])
    st.info("**Accept vs Content-Type:** Accept describes what the client wants back. Content-Type describes the format of the data being sent. Never put real tokens into public examples or GitHub.")
    with st.expander("Mini exercise: choose the right header"):
        h = st.radio("You are sending a JSON body. Which header describes its format?", ["Accept: application/json", "Content-Type: application/json"], key="foundation_header_quiz")
        if st.button("Check header", key="foundation_header_check"):
            (st.success if h.startswith("Content-Type") else st.warning)("Correct: Content-Type describes the request body." if h.startswith("Content-Type") else "Try again: Accept describes the response format you prefer.")

    st.subheader("Lesson 5 · What is a request body?")
    st.markdown("The **body** is the payload: data you send to the server. For example, a shopping app may submit a new product using POST.")
    st.code('POST /products/add HTTP/1.1\nHost: dummyjson.com\nContent-Type: application/json\n\n{"title": "QA Notebook", "price": 25}', language="http")
    st.markdown("The **blank line** separates HTTP headers from the body. Here `title` and `price` are data fields, not headers. GET requests normally send their input in the path or query parameters, not a JSON body.")

    st.subheader("Lesson 6 · What is JSON?")
    st.markdown("**JSON** means **JavaScript Object Notation**. It is a text format used to exchange structured data. Python can read it into dictionaries and lists.")
    st.code('''{
  "id": 1,
  "title": "QA Notebook",
  "price": 25,
  "available": true,
  "tags": ["school", "office"],
  "discount": null
}''', language="json")
    st.markdown("**Types:** `id` and `price` are numbers; `title` is a string; `available` is a boolean; `tags` is an array; `null` means no value. JSON keys and strings use double quotes.")
    st.markdown("**Try editing JSON** — change the title or price, then validate the structure:")
    raw = st.text_area("Editable JSON request body", value='{"title": "QA Notebook", "price": 25, "available": true}', height=110, key="foundation_json")
    if st.button("Validate my JSON", key="foundation_json_validate"):
        try:
            parsed = json.loads(raw)
            st.success("Valid JSON!")
            st.json(parsed)
            if isinstance(parsed, dict):
                st.caption("Fields: " + ", ".join(parsed))
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}")

    st.subheader("Lesson 7 · What is an HTTP response?")
    st.markdown("A **response** is what the server sends back. It includes a status code, response headers and often a JSON body.")
    st.code('HTTP/1.1 200 OK\nContent-Type: application/json\n\n{"id": 1, "title": "QA Notebook", "price": 25}', language="http")
    st.caption("This is a teaching example, not a claim about the live product data.")
    st.table([
        {"Code": "200", "Meaning": "OK: request succeeded"},
        {"Code": "201", "Meaning": "Created: a resource was created"},
        {"Code": "400", "Meaning": "Bad Request: invalid input"},
        {"Code": "401", "Meaning": "Unauthorized: authentication required/invalid"},
        {"Code": "403", "Meaning": "Forbidden: insufficient permission"},
        {"Code": "404", "Meaning": "Not Found: resource missing"},
        {"Code": "500", "Meaning": "Internal Server Error"},
    ])
    st.markdown("**QA insight:** A 404 can be a **passing test** when the test intentionally requests a missing product and expects 404.")

    st.subheader("Lesson 8 · Build a request yourself")
    method = st.selectbox("1. Choose HTTP method", ["GET", "POST", "PUT", "PATCH", "DELETE"], key="foundation_builder_method")
    endpoint = st.selectbox("2. Choose endpoint", ["/products/1", "/products/999999", "/products/add"], key="foundation_builder_endpoint")
    use_json = st.checkbox("3. Include JSON Content-Type header", value=method in ("POST", "PUT", "PATCH"), key="foundation_builder_header")
    body = st.text_area("4. Request body (for POST/PUT/PATCH)", value='{"title":"QA Notebook","price":25}', height=90, disabled=method not in ("POST", "PUT", "PATCH"), key="foundation_builder_body")
    header_lines = ["Host: dummyjson.com", "Accept: application/json"]
    if use_json:
        header_lines.append("Content-Type: application/json")
    preview = f"{method} {endpoint} HTTP/1.1\n" + "\n".join(header_lines)
    if method in ("POST", "PUT", "PATCH"):
        preview += "\n\n" + body
    st.markdown("**Your assembled HTTP request (illustrative preview):**")
    st.code(preview, language="http")
    if st.button("Check my request design", key="foundation_builder_check"):
        problems = []
        if method in ("POST", "PUT", "PATCH"):
            if not use_json:
                problems.append("Include Content-Type: application/json when sending a JSON body.")
            try:
                json.loads(body)
            except json.JSONDecodeError:
                problems.append("The body is not valid JSON.")
        if method == "POST" and endpoint != "/products/add":
            problems.append("For the DummyJSON create example, use POST /products/add.")
        if method in ("PUT", "PATCH", "DELETE") and endpoint == "/products/add":
            problems.append("For an update/delete example, choose a product ID path.")
        if problems:
            for p in problems:
                st.warning(p)
        else:
            st.success("Good request structure! Next, run a real GET scenario in the testing lab below.")
    st.caption("This builder previews a request without sending it. The real API test runner appears after these foundations.")

    st.subheader("Lesson 9 · How a QA engineer tests an API")
    st.markdown("""
**Requirement:** When product 1 is requested, return HTTP 200 and JSON containing `id: 1`.

**Test case:** Send `GET /products/1` → capture response → assert status 200 → assert `id == 1` → report PASS/FAIL.

**Negative case:** Send `GET /products/999999` → expect 404 → PASS if actual equals expected.

**Automation:** Python `requests` sends the HTTP call; `pytest` runs tests; `assert` compares actual vs expected.
""")
    st.code('''import requests

def test_get_product_1():
    response = requests.get("https://dummyjson.com/products/1", timeout=10)
    assert response.status_code == 200
    assert response.json()["id"] == 1''', language="python")
    st.success("Ready for the next section: follow the request through the server, run the real API, then export the pytest test.")
