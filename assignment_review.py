"""Beginner-friendly deterministic grading for API automation assignments.

Only syntax and static code patterns are assessed here. Runtime is assessed by
the existing runner; this is not a secure sandbox or a full hidden-test grader.
"""
import ast
from assignment_help import solution_for

AUTOMATION_STAGES = {"API Automation", "Advanced Automation"}


def _issue(title, why, fix):
    return {"title": title, "why": why, "fix": fix}


def review_automation(module, submission, runtime_ok, runtime_output):
    issues = []
    strengths = []
    try:
        tree = ast.parse(submission)
    except SyntaxError as exc:
        issues.append(_issue(
            f"Syntax error on line {exc.lineno}",
            exc.msg,
            "Check brackets, quotes, colons and indentation near the reported line.",
        ))
        return _result(module, issues, strengths, runtime_output)

    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    names = [n.id for n in ast.walk(tree) if isinstance(n, ast.Name)]
    attrs = [n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)]
    asserts = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    requests_calls = [n for n in calls if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == "requests"]
    methods = {n.func.attr for n in requests_calls}
    source = submission.lower()
    mid = module["id"]

    if not runtime_ok:
        issues.append(_issue("Code did not run successfully",
                             "The execution runner reported an error: " + (runtime_output or "unknown error"),
                             "Read the error message, correct the indicated line, then run the assignment again."))
    else:
        strengths.append("The submitted code ran without a reported exception.")

    if not requests_calls and mid not in {"29", "35", "36"}:
        issues.append(_issue("No requests HTTP call found", "This assignment needs an API request.",
                             "Use requests.get(url, timeout=10) or the method required by the chapter."))
    else:
        strengths.append("An API request call is present.")

    if not asserts and mid != "17":
        issues.append(_issue("Missing assertions", "Printing a response does not prove that it is correct.",
                             "Add assert response.status_code == expected_status and assert a meaningful JSON value."))
    elif asserts:
        strengths.append("At least one Python assert statement is present.")

    status_check = any("status_code" in ast.unparse(a.test) for a in asserts)
    if mid not in {"17", "30", "32", "35", "36"} and not status_check:
        issues.append(_issue("No HTTP status assertion", "The test does not verify the expected status code.",
                             "For example: assert response.status_code == 200 (or 404 for an expected missing resource)."))

    expected_method = {"17":"get","18":"get","19":"get","20":"get","21":"post","22":"patch","23":"delete","24":"get","25":"get","26":"post","27":"get","28":"get"}
    if mid in expected_method and expected_method[mid] not in methods:
        issues.append(_issue("Required HTTP method is missing",
                             f"This module demonstrates requests.{expected_method[mid]}().",
                             f"Add a requests.{expected_method[mid]}(...) call with the chapter endpoint."))

    if mid in {"18", "20", "21", "22", "23", "24", "25", "26", "27"}:
        if not any("json" in ast.unparse(a.test) or "data" in ast.unparse(a.test) or "headers" in ast.unparse(a.test) or "token" in ast.unparse(a.test) for a in asserts):
            issues.append(_issue("Missing response content check",
                                 "The task requires checking the returned data, not just HTTP success.",
                                 "Parse response.json() and assert a chapter-specific field, type, or header."))
    if mid in {"29", "30", "31"} and not any(f.startswith("test_") for f in funcs):
        issues.append(_issue("No pytest test function", "pytest discovers functions named test_*. ",
                             "Define a function such as def test_get_user(): and put assertions inside it."))
    if mid == "30" and "fixture" not in attrs:
        issues.append(_issue("Fixture not found", "This chapter practices reusable pytest setup.",
                             "Use @pytest.fixture to provide a session or test data."))
    if mid == "31" and "parametrize" not in attrs:
        issues.append(_issue("Parametrization not found", "This chapter runs one test with multiple inputs.",
                             "Add @pytest.mark.parametrize('user_id', [1, 2, 3])."))
    if mid == "25" and not any(k.arg == "params" for n in calls for k in n.keywords):
        issues.append(_issue("Query params not supplied", "The assignment is about URL query parameters.",
                             "Pass params={'limit': 5, 'skip': 5} to requests.get()."))
    if mid in {"21", "22", "26"} and not any(k.arg == "json" for n in calls for k in n.keywords):
        issues.append(_issue("JSON request body missing", "The request must send structured data.",
                             "Pass json=payload to requests.post() or requests.patch()."))
    if mid == "27" and "authorization" not in source:
        issues.append(_issue("Authorization header missing", "The protected API needs a bearer token.",
                             "Send headers={'Authorization': f'Bearer {token}'}."))
    if mid == "17":
        prints = [n for n in calls if isinstance(n.func, ast.Name) and n.func.id == "print"]
        printed_expressions = " ".join(ast.unparse(n) for n in prints).lower()
        if not prints:
            issues.append(_issue("Missing print statements",
                                 "This first Python requests assignment explicitly asks you to print two results.",
                                 "Add print('Status:', response.status_code) and print('First name:', response.json()['firstName'])."))
        else:
            if "status_code" not in printed_expressions:
                issues.append(_issue("HTTP status is not printed",
                                     "The task asks for the HTTP status to be visible in the output.",
                                     "Add print('Status:', response.status_code)."))
            if "firstname" not in printed_expressions:
                issues.append(_issue("firstName is not printed",
                                     "The task asks for the user's firstName to be visible in the output.",
                                     "Add print('First name:', response.json()['firstName'])."))
        if not issues:
            strengths.append("Both required values are printed.")
    if mid in {"35", "36"}:
        issues.append(_issue("Project requires instructor review",
                             "A single code snippet cannot establish that a multi-file framework and full test suite work.",
                             "Run python -m pytest -v locally and review the project structure and test report."))
    return _result(module, issues, strengths, runtime_output)


def _result(module, issues, strengths, output):
    passed = not issues
    return {
        "score": 100 if passed else max(0, 70 - 10 * len(issues)),
        "result": "PASS" if passed else "FAIL",
        "strengths": strengths or ["You submitted an attempt."],
        "improvements": [f"{i['title']}: {i['fix']}" for i in issues],
        "issues": issues,
        "feedback": ("All automated checks passed. This is not proof of full API correctness; review expected values and run pytest locally."
                     if passed else "Review the issues below, apply the suggested fixes, and evaluate again."),
        "reference": solution_for(module["id"]),
        "grading_method": "Static checks + existing execution runner",
    }
