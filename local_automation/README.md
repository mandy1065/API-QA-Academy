# VS Code: beginner API automation (independent of Streamlit)

## 1. Install tools on Windows
Install Python 3.11+ from python.org (enable **Add python.exe to PATH**), VS Code from code.visualstudio.com, and VS Code's **Python** extension by Microsoft. Git is optional for running tests but useful for cloning.

Open VS Code → **Terminal → New Terminal** (PowerShell).

## 2. Get the project
If you have Git installed:
```powershell
git clone https://github.com/mandy1065/API-QA-Academy.git
cd API-QA-Academy
```
All course changes are on the default `main` branch. Alternatively, download the repository ZIP from GitHub and extract it. Open the folder in VS Code using **File → Open Folder**.

## 3. Set up the automation environment
```powershell
cd local_automation
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
If PowerShell blocks activation, skip it and run `.venv\Scripts\python.exe -m pip install -r requirements.txt` followed by `.venv\Scripts\python.exe -m pytest -v`.

In VS Code press **Ctrl+Shift+P → Python: Select Interpreter**, then select `local_automation/.venv/Scripts/python.exe`.

## 4. Run and read the results
```powershell
python -m pytest -v
python -m pytest -v tests/test_products.py
python -m pytest -v tests/test_products.py::test_get_product_fields
```
- **PASSED**: actual matches expected.
- **FAILED**: an assertion did not match. Read expected/actual in the traceback.
- **ERROR**: setup, connection, or code failed before the assertion.
- Tests call a live public API, so internet access is required.

## 5. Build a new test from zero
1. Write the requirement: “When product 1 is requested, return 200 and product ID 1.”
2. Define positive and negative scenarios: product 1 → 200; nonexistent product → 404.
3. Add a new file under `tests/` named `test_orders.py` (or copy `test_my_first_api.py`).
4. Write `def test_...():` and use `requests.get(..., timeout=10)`.
5. Assert the HTTP status and at least one JSON field. Do not merely print the response.
6. Run `python -m pytest -v` and fix any failing assertion.
7. Add `@pytest.mark.parametrize` to cover multiple inputs with the same test.
8. Use **Run and Debug** or click the test gutter icon after enabling pytest in the Python extension.

Example:
```python
import requests

def test_missing_product_returns_404():
    response = requests.get("https://dummyjson.com/products/999999", timeout=10)
    assert response.status_code == 404, response.text
```

## 6. What each file does
- `requirements.txt`: Python dependencies.
- `pytest.ini`: tells pytest to find tests in `tests/`.
- `tests/test_products.py`: positive, negative, JSON, query parameter, reusable session and parametrization examples.
- `tests/test_my_first_api.py`: copyable Arrange → Act → Assert template.

## 7. Troubleshooting
- `py is not recognized`: install Python and reopen VS Code; try `python`.
- `No module named pytest`: select the correct interpreter, then install requirements in that environment.
- `collected 0 items`: test files must start with `test_`, and functions must start with `test_`.
- `ModuleNotFoundError: requests`: run `python -m pip install -r requirements.txt`.
- Network timeout / SSL / proxy: verify your connection and organization proxy policy.
- A 404 does **not** automatically mean a failed test; compare with the expected status.

## 8. Streamlit versus VS Code
Streamlit is the interactive classroom and manual API lab. VS Code runs the real pytest files locally. They use the same DummyJSON endpoints and expected outcomes, but VS Code does **not** require Streamlit, OpenAI, or an API key. Never commit real tokens or credentials.

DummyJSON simulates POST/PUT/PATCH/DELETE and does not persist those changes. Do not write tests that assume created data will remain available.
