BASE_URL = "https://dummyjson.com"

STAGES = ["API Foundations", "Manual API Testing", "API Automation", "Advanced Automation"]

MODULES = [
    ("01","API Foundations","What is an API?",30,"Understand what an API is and why QA engineers test it.","GET","/users/1","Client sends a request to an API; the server returns a response.","Client → Request → API/Server → Response","Identify client, API, request, response and status code."),
    ("02","API Foundations","Client, Server & Endpoint",30,"Understand where API calls go.","GET","/products/1","A client calls a server through a specific endpoint.","Base URL = building address; endpoint = room","Compare /products/1 and /users/1."),
    ("03","API Foundations","Request and Response",35,"Read both sides of an API conversation.","GET","/todos/1","Requests can include method, URL, headers, parameters and body; responses contain status, headers and body.","Request = what we ask; response = what comes back","Record status code, headers and three response fields."),
    ("04","API Foundations","HTTP Methods",40,"Know GET, POST, PUT, PATCH and DELETE.","GET","/posts/1","GET reads, POST creates, PUT/PATCH update, DELETE removes.","CRUD: Create POST, Read GET, Update PUT/PATCH, Delete DELETE","Match CRUD actions to HTTP methods."),
    ("05","API Foundations","Status Codes",40,"Understand common success and error codes.","GET","/users/999999","2xx usually means success, 4xx client/request problem, 5xx server problem.","First digit tells the status family","Compare valid and invalid user IDs."),
    ("06","API Foundations","JSON Basics for API Testers",45,"Read JSON objects, arrays and nested data.","GET","/users/1","JSON objects contain key/value pairs; arrays contain ordered values. Python maps these to dicts and lists.","JSON object → dict; JSON array → list","Find strings, numbers, booleans and nested data."),
    ("07","API Foundations","Headers",35,"Understand request and response metadata.","GET","/test","Headers carry metadata such as Content-Type, Accept and Authorization.","Headers travel with the message","Inspect Content-Type and other response headers."),
    ("08","API Foundations","Path vs Query Parameters",40,"Understand URL inputs and filters.","GET","/users?limit=3&skip=0","Path values identify resources; query parameters filter or shape results.","Path = which thing; query = how to filter","Compare limit=2 and limit=5 results."),
    ("09","API Foundations","Authentication Concepts",45,"Understand credentials, tokens and authorization.","POST","/auth/login","Authentication proves identity; authorization controls access. Login often returns an access token.","Credentials → token → protected request","Explain login, token capture and protected access."),

    ("10","Manual API Testing","Manual GET Testing",45,"Test a read endpoint like a QA engineer.","GET","/users/2","Check status, body, important values, data types, headers and response time.","Do not stop at 200; verify the right data","Manually test /users/2 with four checks."),
    ("11","Manual API Testing","Manual POST Testing",50,"Test a create-style request.","POST","/users/add","Send a JSON payload and validate status, returned values and generated id.","Payload → POST → created response","Create a sample user and validate the response."),
    ("12","Manual API Testing","Positive Test Design",40,"Design valid happy-path API tests.","GET","/products/1","Positive tests use valid inputs and confirm expected successful behavior.","Valid request → expected success","Write five positive tests for products."),
    ("13","Manual API Testing","Negative Testing",50,"Challenge the API with invalid inputs.","GET","/users/999999","Negative tests cover invalid IDs, missing data, wrong values, bad credentials and unsupported behavior.","A negative test passes when the API rejects correctly","Design four negative tests."),
    ("14","Manual API Testing","Manual JSON Validation",50,"Validate response structure and important data.","GET","/posts/1","Validate required keys, exact values, types, arrays and nested objects without making tests unnecessarily brittle.","Structure + important values + types","Define six checks for /posts/1."),
    ("15","Manual API Testing","Manual Authentication Testing",60,"Test login and protected access manually.","POST","/auth/login","Validate successful login, token return, protected access, invalid password, missing token and invalid token.","Login → accessToken → Bearer → /auth/me","Execute valid login, invalid login and protected access."),
    ("16","Manual API Testing","API Test Case Design",60,"Turn API requirements into clear test cases.","GET","/users/1","A useful API test case records method, endpoint, setup, inputs, expected status and response checks.","Manual design becomes the automation blueprint","Create ten API test cases across positive, negative, params and auth."),

    ("17","API Automation","Python requests Library",50,"Send API calls from Python.","GET","/users/1","requests.get/post/patch/delete send HTTP calls; Response exposes status_code, headers and json().","Manual Send button becomes requests.get()","Write a GET request and print status plus firstName."),
    ("18","API Automation","Automate GET Testing",55,"Convert manual GET checks into assertions.","GET","/users/2","Call the endpoint, parse JSON and assert status plus important business/data expectations.","Manual check → Python assert","Automate /users/2 with four assertions."),
    ("19","API Automation","Status Code Assertions",45,"Write precise HTTP status assertions.","GET","/users/1","Assert the exact contract when known; do not accept any success code if a specific one is required.","Expected status is part of the API contract","Write one positive and one negative status test."),
    ("20","API Automation","JSON Assertions",60,"Validate API data with Python.","GET","/posts/1","Use response.json() and assert keys, values, list content, nested objects and important types.","Parse once, assert important facts","Write five JSON assertions for /posts/1."),
    ("21","API Automation","POST Automation",60,"Automate create-style requests.","POST","/users/add","Build a Python payload, send json=payload and validate status, id and returned fields.","payload dict → POST → assertions","Automate POST /users/add."),
    ("22","API Automation","PUT & PATCH Automation",55,"Automate update testing.","PATCH","/users/2","PATCH commonly changes selected fields; PUT commonly represents fuller update behavior. Validate changed fields and preserved identity.","Update request → changed response","PATCH a lastName and assert the result."),
    ("23","API Automation","DELETE Automation",45,"Automate deletion behavior.","DELETE","/users/1","Validate delete status and deletion indicators. DummyJSON simulates deletion and returns isDeleted/deletedOn.","Delete → confirmation","Automate DELETE and validate deletion fields."),
    ("24","API Automation","Headers in Automation",45,"Send and inspect HTTP headers in Python.","GET","/test","Use a dict for request headers and response.headers for returned metadata.","headers = metadata dictionary","Send Accept header and inspect Content-Type."),
    ("25","API Automation","Query Parameter Automation",50,"Automate pagination and filters.","GET","/users?limit=3&skip=2","Use params={} to send query parameters and validate returned count plus metadata.","params dict builds query string","Automate limit=5, skip=5."),
    ("26","API Automation","Authentication Automation",70,"Automate login and token capture.","POST","/auth/login","Send sample credentials, assert success and capture accessToken. Real secrets should never be committed to source control.","Login response feeds the next request","Automate login and capture accessToken."),
    ("27","API Automation","Bearer Token & Protected Requests",65,"Call protected endpoints with an access token.","GET","/auth/me","Send Authorization: Bearer <token>, validate authenticated user, then test invalid token behavior.","Token proves authorized access","Automate valid and invalid /auth/me calls."),
    ("28","API Automation","Negative Automation",60,"Automate expected failures.","GET","/users/999999","Assert documented error behavior for invalid resources, credentials and tokens.","Negative test passes when rejection is correct","Automate three negative scenarios."),

    ("29","Advanced Automation","Pytest Basics",70,"Organize API checks as executable tests.","GET","/users/1","pytest discovers test_* functions and uses plain assert statements with useful reporting.","One test function = one behavior","Write three pytest API tests."),
    ("30","Advanced Automation","Fixtures",60,"Reuse setup across tests.","GET","/users/1","Fixtures provide reusable base URLs, sessions, tokens and test data while reducing duplication.","Fixture = reusable setup injected into tests","Create a base_url fixture used by two tests."),
    ("31","Advanced Automation","Parametrization",65,"Run one test against multiple data rows.","GET","/users/1","@pytest.mark.parametrize increases coverage without copying the same test logic.","One test design + many input rows","Parametrize user IDs 1, 2 and 3."),
    ("32","Advanced Automation","Reusable API Functions",70,"Separate request logic from test logic.","GET","/users/1","Create functions or client methods such as get_user(), create_user() and login(). Tests then focus on intent and assertions.","Client layer sends; test layer verifies","Build get_user and get_users helpers."),
    ("33","Advanced Automation","Timeouts & Error Handling",60,"Make API tests fail safely and clearly.","GET","/test","Use timeout= and handle only meaningful request exceptions. Good tests fail with clear messages instead of hanging.","Reliable automation expects networks can fail","Add timeouts to reusable functions."),
    ("34","Advanced Automation","Test Data Management",65,"Organize reusable API test data.","POST","/users/add","Keep reusable payloads separate when helpful. Use fixtures, Python data or JSON files, and never commit real secrets.","Tests describe behavior; data supports scenarios","Move two payloads into reusable test data."),
    ("35","Advanced Automation","API Automation Framework",90,"Build a maintainable automation project.","GET","/users/1","Separate config, clients, tests, data and fixtures. Keep abstractions simple and focused on repeated behavior.","config → clients → tests","Design a framework and implement five tests."),
    ("36","Advanced Automation","Final Project — Production-Style API Suite",150,"Combine manual QA thinking and framework skills.","GET","/users/1","Build a DummyJSON suite with authentication, CRUD simulation, query parameters, positive/negative coverage, reusable clients, fixtures, parametrization, timeouts and reporting.","Requirements → manual proof → automation → framework","Build at least 12 tests covering auth, CRUD, params, JSON and negative cases."),
]


def expanded_modules():
    rows = []
    for module_id, stage, title, minutes, goal, method, path, learn, mental, assignment in MODULES:
        rows.append({
            "id": module_id,
            "stage": stage,
            "title": title,
            "minutes": minutes,
            "goal": goal,
            "method": method,
            "path": path,
            "learn": learn,
            "mental": mental,
            "assignment": assignment,
        })
    return rows
