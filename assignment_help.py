"""Progressive assignment hints and reference solutions for automation lessons."""
from chapter_walkthroughs import DETAILS
from assignment_examples import EXAMPLES

HINTS = {
"17": ["Import requests and send GET /users/1 with timeout=10.", "Read response.status_code and response.json()[\'firstName\'].", "Use print() for both values. For example: print(\'Status:\', response.status_code)."],
"18": ["Define a test_ function.", "Use requests.get('/users/2') with the full URL.", "Assert status_code == 200 and response.json()['id'] == 2."],
"19": ["Write one valid-ID and one missing-ID test.", "Use exact status assertions.", "An expected 404 counts as a passing negative test."],
"20": ["Parse response.json() once into data.", "Check 'id' and 'title' keys.", "Use isinstance() to validate data types."],
"21": ["Build a Python dictionary payload.", "Pass it with json=payload to requests.post().", "Assert status 201 and verify returned firstName."],
"22": ["Use requests.patch() with a JSON body.", "Target /users/2 and set lastName.", "Assert status, updated field and user ID."],
"23": ["Use requests.delete() on /users/1.", "Assert HTTP 200.", "Assert response.json()['isDeleted'] is True."],
"24": ["Create a headers dictionary.", "Pass headers= to requests.get().", "Inspect response.headers['Content-Type']."],
"25": ["Use params={'limit':5,'skip':5}.", "Read JSON metadata.", "Assert limit and skip values."],
"26": ["POST the DummyJSON sample login credentials.", "Check HTTP status before reading JSON.", "Check accessToken exists; never print the token."],
"27": ["Login first and save accessToken.", "Pass Authorization: Bearer <token>.", "Call /auth/me and assert success."],
"28": ["Use an ID that does not exist.", "GET /users/999999.", "Assert status_code == 404."],
"29": ["Create a file named test_products.py.", "Write a function starting with test_.", "Run python -m pytest -v."],
"30": ["Import pytest.", "Use @pytest.fixture to provide a requests.Session().", "Inject the fixture into a test function."],
"31": ["Import pytest.", "Use @pytest.mark.parametrize('user_id',[1,2,3]).", "Assert returned id matches each parameter."],
"32": ["Move the HTTP call into get_user(user_id).", "Return the response from the helper.", "Keep assert statements in the test function."],
"33": ["Always supply timeout=10.", "Let network exceptions fail clearly.", "Don't swallow failed assertions."],
"34": ["Create a fixture returning a test payload.", "Pass it into a POST test.", "Check the response fields match the payload."],
"35": ["Separate tests, clients and fixtures.", "Put shared setup in conftest.py.", "Run the full suite with python -m pytest -v."],
"36": ["Plan positive and negative test cases.", "Cover CRUD, auth, parameters and JSON checks.", "Use fixtures, parametrization and reusable clients; run the suite and record results."],
}

def hints_for(module_id):
    return HINTS.get(module_id, ["Review the worked example.", "Translate each requirement into an assertion.", "Compare actual and expected results."])

def solution_for(module_id):
    if module_id in EXAMPLES:
        return EXAMPLES[module_id]
    return DETAILS[module_id][5] or "# Multi-file project: follow the local_automation README and submit your test report."


def explanation_for(module_id):
    if module_id in {"35","36"}:
        return "This is a reference starting point, not a complete final project. Combine the chapter's steps with the local_automation example framework."
    return "Use this as a reference after attempting the assignment. Compare the request, timeout, response parsing and assertions with your own work."
