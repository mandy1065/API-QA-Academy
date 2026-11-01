"""Regression checks for the entire 36-module curriculum.

Run: python -m pytest -q tests/test_curriculum_consistency.py
No live API requests are made by these tests.
"""
import ast
import pytest

from lessons import expanded_modules, STAGES
from chapter_content import FOUNDATION, MANUAL, AUTOMATION, chapter_material, chapter_quiz
from chapter_walkthroughs import DETAILS
from assignment_help import HINTS, solution_for
from assignment_examples import EXAMPLES
from assignment_review import review_automation


MODULES = expanded_modules()
IDS = {module["id"] for module in MODULES}


def test_all_36_modules_have_unique_sequential_ids():
    assert len(MODULES) == 36
    assert [m["id"] for m in MODULES] == [f"{i:02d}" for i in range(1, 37)]
    assert {m["stage"] for m in MODULES} == set(STAGES)


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m["id"])
def test_every_chapter_has_unique_learning_material(module):
    mid = module["id"]
    assert mid in DETAILS
    story, steps, request, response, checks, code = DETAILS[mid]
    assert len(story.strip()) > 35
    assert len(steps) >= 4
    assert request.strip() and response.strip()
    assert len(checks) >= 2
    assert chapter_material(module)[0]
    q, options, correct = chapter_quiz(module)
    assert q and len(options) >= 3 and 0 <= correct < len(options)
    assert module["goal"] and module["assignment"] and module["method"] and module["path"]


def test_stage_counts_and_manual_methods():
    assert sum(m["stage"] == "API Foundations" for m in MODULES) == 9
    assert sum(m["stage"] == "Manual API Testing" for m in MODULES) == 7
    assert sum(m["stage"] == "API Automation" for m in MODULES) == 12
    assert sum(m["stage"] == "Advanced Automation" for m in MODULES) == 8
    assert {m["method"] for m in MODULES if m["stage"] == "Manual API Testing"} >= {"GET", "POST", "PATCH", "DELETE"}
    assert "PUT" in MODULES[11]["assignment"]


@pytest.mark.parametrize("mid", [f"{i:02d}" for i in range(17, 37)])
def test_every_automation_assignment_has_hints(mid):
    assert mid in HINTS
    assert len(HINTS[mid]) >= 3
    assert all(h.strip() for h in HINTS[mid])


@pytest.mark.parametrize("mid", [f"{i:02d}" for i in range(17, 35)])
def test_reference_solutions_are_valid_python(mid):
    assert mid in EXAMPLES
    solution = solution_for(mid)
    assert solution == EXAMPLES[mid]
    tree = ast.parse(solution)
    assert any(isinstance(n, ast.Call) for n in ast.walk(tree))


@pytest.mark.parametrize("mid", [f"{i:02d}" for i in range(17, 29)])
def test_basic_automation_references_pass_static_grader(mid):
    module = next(m for m in MODULES if m["id"] == mid)
    result = review_automation(module, solution_for(mid), True, "Mock successful execution")
    assert result["result"] == "PASS", (mid, result["issues"])


@pytest.mark.parametrize("mid", [f"{i:02d}" for i in range(29, 35)])
def test_advanced_references_require_local_pytest_verification(mid):
    module = next(m for m in MODULES if m["id"] == mid)
    result = review_automation(module, solution_for(mid), True, "Static only")
    assert result["result"] == "NEEDS LOCAL TEST", (mid, result["issues"])


def test_module_17_solution_prints_both_required_values():
    solution = solution_for("17")
    tree = ast.parse(solution)
    prints = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "print"]
    rendered = " ".join(ast.unparse(n) for n in prints).lower()
    assert "status_code" in rendered
    assert "firstname" in rendered


def test_missing_module_17_prints_fail():
    module = next(m for m in MODULES if m["id"] == "17")
    incomplete = 'import requests\nr = requests.get("https://dummyjson.com/users/1")\nassert r.status_code == 200'
    result = review_automation(module, incomplete, True, "Mock")
    assert result["result"] == "FAIL"
    assert any("print" in issue["title"].lower() for issue in result["issues"])


def test_advanced_project_cannot_be_marked_pass_without_full_review():
    for mid in ("35", "36"):
        module = next(m for m in MODULES if m["id"] == mid)
        result = review_automation(module, "import requests\nassert True", True, "Static")
        assert result["result"] != "PASS"


def test_every_api_automation_module_has_manual_to_automation_case():
    from manual_to_automation import CASES
    ids = {m["id"] for m in MODULES if m["stage"] == "API Automation"}
    assert set(CASES) == ids
    for mid, (title, method, path, body, expected, checks) in CASES.items():
        assert title and method in {"GET", "POST", "PUT", "PATCH", "DELETE"}
        assert path.startswith("/")
        assert isinstance(expected, int)
        assert len(checks) >= 1
        assert solution_for(mid).strip()


def test_manual_automation_response_assertions():
    from manual_to_automation import _evaluate
    samples = [
        ("17", 200, {"id": 1, "firstName": "Emily"}, {}, True),
        ("17", 200, {"id": 2, "firstName": ""}, {}, False),
        ("21", 201, {"id": 209, "firstName": "Alex", "age": 30}, {}, True),
        ("21", 200, {"id": 209, "firstName": "Alex", "age": 30}, {}, False),
        ("23", 200, {"id": 1, "isDeleted": True, "deletedOn": "2026-01-01"}, {}, True),
        ("24", 200, {}, {"Content-Type": "application/json; charset=utf-8"}, True),
        ("25", 200, {"limit": 5, "skip": 5, "users": [1, 2]}, {}, True),
        ("27", 401, {"message": "Unauthorized"}, {}, True),
        ("27", 200, {"id": 1}, {}, False),
        ("28", 404, {"message": "User not found"}, {}, True),
    ]
    for mid, status, body, headers, expected_pass in samples:
        result = _evaluate(mid, status, body, headers)
        assert all(passed for _, passed in result) is expected_pass, (mid, result)
