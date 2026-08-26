import ast
import contextlib
import io
import json
import time
from datetime import datetime
from types import SimpleNamespace
from urllib.parse import urlparse

import pandas as pd
import requests
import streamlit as st
from openai import OpenAI

from lessons import BASE_URL, STAGES, expanded_modules

st.set_page_config(page_title="API QA Academy", page_icon="🔌", layout="wide")

MODEL = st.secrets.get("OPENAI_MODEL", "gpt-5.4-nano")
PASS_SCORE = 70
MODULES = expanded_modules()

# ---------- UI ----------
st.markdown(
    """
    <style>
    .stApp{background:radial-gradient(circle at 0% 0%,rgba(37,99,235,.10),transparent 28%),radial-gradient(circle at 100% 0%,rgba(14,165,233,.10),transparent 25%),#f8fafc;}
    .block-container{max-width:1280px;padding-top:1.2rem;padding-bottom:3rem;}
    .hero{background:linear-gradient(135deg,#0f172a 0%,#172554 50%,#0c4a6e 100%);padding:26px 30px;border-radius:24px;color:white;box-shadow:0 18px 45px rgba(15,23,42,.18);margin-bottom:16px;}
    .hero h1{margin:0;font-size:31px;letter-spacing:-.02em}.hero p{margin:.4rem 0 0;color:#cbd5e1}
    .chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.chip{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);padding:6px 10px;border-radius:999px;font-size:12px;font-weight:700}
    .stage{font-size:12px;font-weight:850;letter-spacing:.08em;text-transform:uppercase;color:#2563eb}.lesson-title{font-size:25px;font-weight:850;color:#0f172a;margin:.1rem 0}.subtle{color:#64748b}
    .card{background:white;border:1px solid #e2e8f0;border-radius:16px;padding:16px 18px;box-shadow:0 4px 16px rgba(15,23,42,.04);margin:8px 0 14px}
    .mental{background:#eff6ff;border-left:4px solid #2563eb;border-radius:12px;padding:13px 15px;margin:10px 0}.qa-note{background:#ecfeff;border:1px solid #a5f3fc;border-radius:14px;padding:13px 15px;margin:10px 0}
    .flow{background:#0f172a;color:#dbeafe;padding:14px 16px;border-radius:14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap}.console{background:#020617;color:#e2e8f0;border-radius:14px;padding:14px 16px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;max-height:430px;overflow:auto}
    .method{display:inline-block;padding:4px 9px;border-radius:8px;background:#dbeafe;color:#1d4ed8;font-size:12px;font-weight:850;margin-right:6px}
    div[data-testid="stMetric"]{background:white;border:1px solid #e2e8f0;border-radius:15px;padding:12px 14px;box-shadow:0 4px 14px rgba(15,23,42,.04)}
    .stTabs [data-baseweb="tab-list"]{gap:7px;background:#eaf0f7;padding:6px;border-radius:14px}.stTabs [data-baseweb="tab"]{border-radius:10px;height:42px;font-weight:750}.stTabs [aria-selected="true"]{background:white!important;box-shadow:0 2px 8px rgba(15,23,42,.08)}
    .stButton>button,.stDownloadButton>button{border-radius:12px;font-weight:750}div[data-testid="stTextArea"] textarea{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;border-radius:12px!important}footer{visibility:hidden}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Helpers ----------
def is_dummyjson_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme == "https" and parsed.hostname == "dummyjson.com"
    except Exception:
        return False


def full_url(path_or_url: str) -> str:
    value = (path_or_url or "").strip()
    if value.startswith("http://") or value.startswith("https://"):
        return value
    if not value.startswith("/"):
        value = "/" + value
    return BASE_URL + value


def send_api(method, path, headers=None, body=None, timeout=10):
    url = full_url(path)
    if not is_dummyjson_url(url):
        raise ValueError("This classroom playground only allows https://dummyjson.com endpoints.")
    started = time.perf_counter()
    response = requests.request(
        method.upper(),
        url,
        headers=headers or {},
        json=body if method.upper() in {"POST", "PUT", "PATCH"} else None,
        timeout=timeout,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    try:
        data = response.json()
    except Exception:
        data = response.text
    return response, data, elapsed_ms


def pretty(data):
    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=2, ensure_ascii=False)
    return str(data)


def lesson_terms(module):
    title = module["title"].lower()
    mapping = {
        "api": ["API", "client", "server", "request", "response", "endpoint"],
        "status": ["2xx success", "4xx client error", "5xx server error", "expected vs actual"],
        "json": ["object/dict", "array/list", "key", "value", "nested data"],
        "header": ["Content-Type", "Accept", "Authorization", "Bearer"],
        "auth": ["credentials", "access token", "refresh token", "Bearer header"],
        "pytest": ["test_ function", "assert", "discovery", "reporting"],
        "fixture": ["setup", "reuse", "scope", "conftest.py"],
        "param": ["data-driven", "multiple inputs", "one test design"],
        "framework": ["config", "clients", "tests", "fixtures", "test data"],
    }
    for key, terms in mapping.items():
        if key in title:
            return terms
    return ["expected result", "actual result", "assertion", "coverage"]


def common_mistakes(module):
    title = module["title"].lower()
    if "status" in title:
        return ["Checking only that a response exists", "Accepting any 2xx when the contract expects one exact code", "Ignoring error-body validation"]
    if "json" in title:
        return ["Asserting every dynamic field", "Confusing an object/dict with an array/list", "Forgetting nested keys can be missing"]
    if "auth" in title or "bearer" in title:
        return ["Committing real passwords/tokens", "Forgetting the 'Bearer ' prefix", "Testing only valid login and no invalid-token case"]
    if "post" in title or "patch" in title or "put" in title:
        return ["Sending malformed JSON", "Forgetting Content-Type/json payload", "Checking status but not returned field values"]
    if "pytest" in title:
        return ["Putting many unrelated behaviors in one test", "Using print instead of assertions", "Giving tests unclear names"]
    return ["Testing only the happy path", "Checking only status code", "Not writing a clear expected result"]


def quiz_for(module):
    title = module["title"].lower()
    bank = [
        ("Which HTTP method normally reads data?", ["GET", "POST", "DELETE", "PATCH"], "GET"),
        ("Which part summarizes the HTTP result?", ["Status code", "Variable name", "Python comment", "Folder name"], "Status code"),
        ("What should QA compare?", ["Expected vs actual", "Only screenshots", "Only endpoint names", "Only code length"], "Expected vs actual"),
    ]
    if "auth" in title or "bearer" in title:
        return ("What is commonly sent after 'Bearer' in Authorization?", ["Access token", "Status code", "URL", "JSON key"], "Access token")
    if "json" in title:
        return ("A JSON object usually becomes what in Python?", ["dict", "int", "tuple only", "HTTP status"], "dict")
    if "query" in title or "path" in title:
        return ("Which is a query parameter?", ["?limit=5", "/users/5", "200", "Bearer"], "?limit=5")
    if "pytest" in title:
        return ("What function prefix does pytest commonly discover?", ["test_", "run_", "qa_", "case_"], "test_")
    return bank[int(module["id"]) % len(bank)]


def sample_code(module):
    path = module["path"]
    method = module["method"]
    if module["id"] == "26":
        return '''import requests\n\npayload = {\n    "username": "emilys",\n    "password": "emilyspass"\n}\nresponse = requests.post("https://dummyjson.com/auth/login", json=payload, timeout=10)\nprint(response.status_code)\nprint("token returned:", "accessToken" in response.json())'''
    if module["id"] == "27":
        return '''import requests\n\nlogin = requests.post(\n    "https://dummyjson.com/auth/login",\n    json={"username":"emilys","password":"emilyspass"},\n    timeout=10\n)\ntoken = login.json()["accessToken"]\nheaders = {"Authorization": f"Bearer {token}"}\nresponse = requests.get("https://dummyjson.com/auth/me", headers=headers, timeout=10)\nprint(response.status_code)\nprint(response.json()["username"])'''
    if module["id"] == "29":
        return '''import requests\n\ndef test_get_user():\n    response = requests.get("https://dummyjson.com/users/1", timeout=10)\n    assert response.status_code == 200\n    assert response.json()["id"] == 1'''
    if method == "POST":
        return f'''import requests\n\npayload = {{"firstName": "Alex", "age": 30}}\nresponse = requests.post("{BASE_URL}{path}", json=payload, timeout=10)\nprint(response.status_code)\nprint(response.json())'''
    if method in {"PUT", "PATCH"}:
        return f'''import requests\n\npayload = {{"lastName": "Automation"}}\nresponse = requests.{method.lower()}("{BASE_URL}{path}", json=payload, timeout=10)\nprint(response.status_code)\nprint(response.json())'''
    if method == "DELETE":
        return f'''import requests\n\nresponse = requests.delete("{BASE_URL}{path}", timeout=10)\nprint(response.status_code)\nprint(response.json())'''
    return f'''import requests\n\nresponse = requests.get("{BASE_URL}{path}", timeout=10)\nprint(response.status_code)\ndata = response.json()\nprint(data)'''


class SafeRequests:
    @staticmethod
    def _check(url):
        if not is_dummyjson_url(url):
            raise ValueError("Only https://dummyjson.com is allowed in this classroom runner.")
    @classmethod
    def get(cls, url, **kwargs):
        cls._check(url); kwargs.setdefault("timeout", 10); return requests.get(url, **kwargs)
    @classmethod
    def post(cls, url, **kwargs):
        cls._check(url); kwargs.setdefault("timeout", 10); return requests.post(url, **kwargs)
    @classmethod
    def put(cls, url, **kwargs):
        cls._check(url); kwargs.setdefault("timeout", 10); return requests.put(url, **kwargs)
    @classmethod
    def patch(cls, url, **kwargs):
        cls._check(url); kwargs.setdefault("timeout", 10); return requests.patch(url, **kwargs)
    @classmethod
    def delete(cls, url, **kwargs):
        cls._check(url); kwargs.setdefault("timeout", 10); return requests.delete(url, **kwargs)
    @classmethod
    def request(cls, method, url, **kwargs):
        cls._check(url); kwargs.setdefault("timeout", 10); return requests.request(method, url, **kwargs)


SAFE_REQUESTS_MODULE = SimpleNamespace(get=SafeRequests.get, post=SafeRequests.post, put=SafeRequests.put, patch=SafeRequests.patch, delete=SafeRequests.delete, request=SafeRequests.request)
ALLOWED_BUILTINS = {"print":print,"len":len,"str":str,"int":int,"float":float,"bool":bool,"dict":dict,"list":list,"range":range,"type":type,"isinstance":isinstance,"sum":sum,"min":min,"max":max,"abs":abs,"enumerate":enumerate}
BLOCKED_NAMES = {"eval","exec","open","compile","globals","locals","vars","input","help","dir","getattr","setattr","delattr","breakpoint"}


def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "requests":
        return SAFE_REQUESTS_MODULE
    raise ImportError("Only the requests module is available in this classroom runner.")


def validate_student_code(code):
    if len(code) > 8000:
        return False, "Code is too long for this practice runner."
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"Syntax error line {exc.lineno}: {exc.msg}"
    blocked = (ast.ClassDef, ast.With, ast.AsyncWith, ast.AsyncFunctionDef, ast.Await, ast.Yield, ast.YieldFrom, ast.Global, ast.Nonlocal, ast.Delete)
    for node in ast.walk(tree):
        if isinstance(node, blocked):
            return False, f"{type(node).__name__} is not needed in this course runner."
        if isinstance(node, ast.Import):
            if any(alias.name != "requests" for alias in node.names):
                return False, "Only import requests is allowed."
        if isinstance(node, ast.ImportFrom):
            return False, "Use import requests rather than from-import statements."
        if isinstance(node, ast.Name) and (node.id.startswith("__") or node.id in BLOCKED_NAMES):
            return False, f"'{node.id}' is not allowed."
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return False, "Special Python attributes are not allowed."
    return True, ""


def run_student_code(code):
    ok, message = validate_student_code(code)
    if not ok:
        return False, message
    output = io.StringIO()
    builtins = dict(ALLOWED_BUILTINS)
    builtins["__import__"] = safe_import
    env = {"__builtins__": builtins}
    try:
        with contextlib.redirect_stdout(output):
            exec(compile(code, "<student_api_code>", "exec"), env, env)
        text = output.getvalue().rstrip()
        return True, (text[:8000] + ("\n...output shortened..." if len(text) > 8000 else "")) or "(Code ran successfully. No printed output.)"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def local_grade(module, submission, output=""):
    text = (submission + "\n" + output).lower()
    score = 35
    strengths, improvements = [], []
    if len(submission.strip()) > 80:
        score += 15; strengths.append("You provided a meaningful attempt.")
    if any(x in text for x in ["status", "status_code", "200", "404"]):
        score += 15; strengths.append("You considered HTTP status behavior.")
    if any(x in text for x in ["json", "response", "assert", "expected"]):
        score += 15; strengths.append("You included response or validation thinking.")
    if module["stage"] in {"API Automation", "Advanced Automation"} and "assert" not in text and "pytest" not in text:
        improvements.append("Add explicit assertions so the automation can decide PASS/FAIL.")
    else:
        score += 10
    if "negative" in module["title"].lower() and not any(x in text for x in ["invalid", "404", "401", "wrong", "missing"]):
        improvements.append("Include a clear invalid-input or expected-error case.")
    score = min(score, 100)
    if not improvements:
        improvements.append("Add one more edge or negative check to strengthen coverage.")
    return {"score":score,"result":"PASS" if score >= PASS_SCORE else "KEEP PRACTICING","strengths":strengths or ["You attempted the required task."],"improvements":improvements,"feedback":"The local evaluator checked completion, API terminology and validation thinking."}


def ai_grade(module, submission, output=""):
    key = st.secrets.get("OPENAI_API_KEY")
    if not key:
        return local_grade(module, submission, output)
    prompt = f"""
You are a patient senior API QA automation instructor grading a student.
The student is progressing from beginner concepts to advanced API automation.
Grade only the assigned module and be technically accurate. Reward testing thinking, not unnecessary complexity.

MODULE: {module['id']} - {module['title']}
STAGE: {module['stage']}
GOAL: {module['goal']}
ASSIGNMENT: {module['assignment']}
STUDENT SUBMISSION:\n{submission}
EXECUTION OUTPUT (if any):\n{output}

Score using: concept correctness 25, test design/coverage 25, expected-vs-actual validation 20, implementation quality 20, clarity 10.
For automation modules, penalize code that only prints responses without meaningful assertions when assertions are expected.
Return ONLY JSON:
{{"score":0,"result":"PASS","strengths":["..."],"improvements":["..."],"feedback":"2-4 beginner-friendly sentences"}}
70+ is PASS.
""".strip()
    try:
        response = OpenAI(api_key=key).responses.create(model=MODEL, input=prompt)
        raw = response.output_text.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(raw)
        data["score"] = max(0, min(100, int(data.get("score", 0))))
        data["result"] = "PASS" if data["score"] >= PASS_SCORE else "KEEP PRACTICING"
        return data
    except Exception:
        return local_grade(module, submission, output)

# ---------- State ----------
for key, default in {
    "student_name":"", "student_id":"", "completed":{}, "quiz_done":{}, "assignment_results":{}, "playground_history":[]
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <h1>🔌 API QA Academy</h1>
  <p>From zero API knowledge → manual API testing → Python automation → pytest framework.</p>
  <div class="chips"><span class="chip">36 guided modules</span><span class="chip">🌐 Live DummyJSON lab</span><span class="chip">🐍 Python runner</span><span class="chip">🔐 Authentication</span><span class="chip">🤖 AI evaluation</span></div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎓 Student")
    st.session_state.student_name = st.text_input("Name", value=st.session_state.student_name)
    st.session_state.student_id = st.text_input("Student ID / Email", value=st.session_state.student_id)
    st.divider()
    st.markdown("### 🧭 Learning Path")
    selected_stage = st.selectbox("Stage", STAGES)
    stage_modules = [m for m in MODULES if m["stage"] == selected_stage]
    labels = [f"{m['id']}. {m['title']} · {m['minutes']} min" for m in stage_modules]
    selected_label = st.radio("Module", labels, label_visibility="collapsed")
    module = stage_modules[labels.index(selected_label)]
    passed = sum(1 for m in MODULES if st.session_state.completed.get(m["id"]))
    st.progress(passed / len(MODULES), text=f"Course progress: {passed}/{len(MODULES)} passed")

# metrics
c1,c2,c3,c4 = st.columns(4)
c1.metric("Module", f"{module['id']} / {len(MODULES)}")
c2.metric("Stage", STAGES.index(module["stage"]) + 1)
c3.metric("Estimated", f"{module['minutes']} min")
c4.metric("Passed", sum(1 for v in st.session_state.completed.values() if v))

st.markdown(f'<div class="stage">{module["stage"]}</div><div class="lesson-title">Module {module["id"]} — {module["title"]}</div><div class="subtle">Goal: {module["goal"]}</div>', unsafe_allow_html=True)

learn_tab, lab_tab, practice_tab, assignment_tab, progress_tab = st.tabs(["📘 Learn", "🌐 API Lab", "🧪 Practice", "📝 Assignment", "📊 Progress"])

# ---------- Learn ----------
with learn_tab:
    st.markdown("### 1. Understand the concept")
    st.markdown(f'<div class="card">{module["learn"]}</div>', unsafe_allow_html=True)
    st.markdown("### 2. Think about it this way")
    st.markdown(f'<div class="mental">💡 {module["mental"]}</div>', unsafe_allow_html=True)

    if module["stage"] == "API Foundations":
        st.markdown("### 3. The API conversation")
        st.markdown('<div class="flow">Client / Tester\n      ↓ request\nDummyJSON API / Server\n      ↓ response\nStatus + Headers + JSON Body</div>', unsafe_allow_html=True)
    elif module["stage"] == "Manual API Testing":
        st.markdown("### 3. How a tester thinks")
        st.markdown('<div class="flow">Requirement\n   ↓\nBuild request\n   ↓\nSend manually\n   ↓\nCompare EXPECTED vs ACTUAL\n   ↓\nPASS / FAIL / DEFECT</div>', unsafe_allow_html=True)
    else:
        st.markdown("### 3. From manual check to automation")
        st.markdown('<div class="flow">Manual test case\n   ↓\nPython requests\n   ↓\nresponse.status_code / response.json()\n   ↓\nassert expected == actual\n   ↓\npytest result</div>', unsafe_allow_html=True)

    st.markdown("### 4. Key terms")
    cols = st.columns(min(4, len(lesson_terms(module))))
    for i, term in enumerate(lesson_terms(module)):
        cols[i % len(cols)].markdown(f'<div class="card"><b>{term}</b></div>', unsafe_allow_html=True)

    st.markdown("### 5. Real example")
    st.markdown(f'<span class="method">{module["method"]}</span><b>{BASE_URL}{module["path"]}</b>', unsafe_allow_html=True)
    if module["stage"] in {"API Automation", "Advanced Automation"}:
        st.code(sample_code(module), language="python")
    else:
        st.code(f"{module['method']} {BASE_URL}{module['path']}", language="text")

    with st.expander("Common beginner mistakes", expanded=False):
        for item in common_mistakes(module):
            st.write("⚠️ " + item)

    st.markdown("### 6. Quick knowledge check")
    q, options, answer = quiz_for(module)
    choice = st.radio(q, options, key=f"quiz_{module['id']}")
    if st.button("Check Answer", key=f"checkquiz_{module['id']}"):
        if choice == answer:
            st.success("✅ Correct — concept check passed.")
            st.session_state.quiz_done[module["id"]] = True
        else:
            st.error("Not quite. Review the explanation above and try again.")

# ---------- Lab ----------
with lab_tab:
    st.markdown("### Live DummyJSON API Playground")
    st.caption("Use this like a lightweight Postman inside the course. Only DummyJSON endpoints are allowed.")
    p1,p2 = st.columns([1,3])
    method = p1.selectbox("Method", ["GET","POST","PUT","PATCH","DELETE"], index=["GET","POST","PUT","PATCH","DELETE"].index(module["method"]) if module["method"] in ["GET","POST","PUT","PATCH","DELETE"] else 0, key=f"method_{module['id']}")
    path = p2.text_input("Endpoint", value=module["path"], key=f"path_{module['id']}")
    headers_text = st.text_area("Headers (JSON)", value='{"Accept":"application/json"}', height=90, key=f"headers_{module['id']}")
    default_body = '{\n  "firstName": "Alex",\n  "age": 30\n}' if method in {"POST","PUT","PATCH"} else "{}"
    body_text = st.text_area("Request Body (JSON)", value=default_body, height=130, disabled=method not in {"POST","PUT","PATCH"}, key=f"body_{module['id']}")
    if st.button("🚀 Send Request", type="primary", use_container_width=True, key=f"send_{module['id']}"):
        try:
            headers = json.loads(headers_text or "{}")
            body = json.loads(body_text or "{}") if method in {"POST","PUT","PATCH"} else None
            response, data, elapsed_ms = send_api(method, path, headers=headers, body=body)
            st.session_state[f"lab_result_{module['id']}"] = {"status":response.status_code,"time":elapsed_ms,"headers":dict(response.headers),"data":data,"url":response.url}
            st.session_state.playground_history.append({"time":datetime.now().isoformat(timespec="seconds"),"method":method,"url":response.url,"status":response.status_code,"ms":elapsed_ms})
        except Exception as exc:
            st.error(f"Request error: {exc}")

    result = st.session_state.get(f"lab_result_{module['id']}")
    if result:
        r1,r2,r3 = st.columns(3)
        r1.metric("Status", result["status"])
        r2.metric("Response Time", f"{result['time']} ms")
        r3.metric("Method", method)
        st.markdown("**Response Body**")
        st.markdown(f'<div class="console">{pretty(result["data"])}</div>', unsafe_allow_html=True)
        with st.expander("Response headers"):
            st.json(result["headers"])
        st.markdown('<div class="qa-note"><b>QA habit:</b> Before calling it PASS, compare the actual status/body to an expected result.</div>', unsafe_allow_html=True)

# ---------- Practice ----------
with practice_tab:
    if module["stage"] in {"API Foundations", "Manual API Testing"}:
        st.markdown("### Guided manual practice")
        st.write("Use the **API Lab** first, then write what you observed and what you would validate.")
        prompt = f"Practice task: {module['assignment']}"
        st.info(prompt)
        practice_answer = st.text_area("Your observations / checks", height=220, key=f"manualpractice_{module['id']}", placeholder="Expected status:\nActual status:\nJSON checks:\nPASS/FAIL:\nWhat else would you test?")
        if st.button("Check My Practice", type="primary", key=f"manualcheck_{module['id']}"):
            if len(practice_answer.strip()) < 50:
                st.warning("Add a little more detail: expected result, actual result and at least two checks.")
            else:
                st.success("✅ Good practice attempt. Compare your checks with the Learn section, then move to the assignment.")
                if not any(word in practice_answer.lower() for word in ["expected", "status", "pass", "fail"]):
                    st.info("Tip: always write the expected result and explicit PASS/FAIL decision.")
    else:
        st.markdown("### Python API practice")
        st.caption("This runner permits Python plus the requests module, and restricts requests to dummyjson.com.")
        code_key = f"practice_code_{module['id']}"
        if code_key not in st.session_state:
            st.session_state[code_key] = sample_code(module)
        code = st.text_area("Edit the code", key=code_key, height=340)
        p1,p2 = st.columns(2)
        run_code = p1.button("▶ Run Practice", type="primary", use_container_width=True, key=f"runpractice_{module['id']}")
        if p2.button("↺ Reset Example", use_container_width=True, key=f"resetpractice_{module['id']}"):
            st.session_state[code_key] = sample_code(module)
            st.rerun()
        if run_code:
            ok, output = run_student_code(code)
            st.session_state[f"practice_output_{module['id']}"] = output
            if ok:
                st.success("Code ran successfully.")
            else:
                st.error("Your code did not run yet. Use the error message to fix it.")
        if f"practice_output_{module['id']}" in st.session_state:
            st.markdown("#### Output")
            st.markdown(f'<div class="console">{st.session_state[f"practice_output_{module["id"]}"]}</div>', unsafe_allow_html=True)
        with st.expander("Need a hint?"):
            st.write("Start from the working example. Change one thing at a time. For automated tests, add explicit assertions for the expected status and important JSON values.")

# ---------- Assignment ----------
with assignment_tab:
    st.markdown("### Module Assignment")
    st.markdown(f'<div class="card"><b>Task</b><br>{module["assignment"]}</div>', unsafe_allow_html=True)
    st.markdown("**Evaluation looks for:** concept correctness · expected vs actual thinking · API validation · coverage · clarity")
    if module["stage"] in {"API Automation", "Advanced Automation"}:
        assignment_key = f"assignment_code_{module['id']}"
        if assignment_key not in st.session_state:
            st.session_state[assignment_key] = "# Write your assignment solution here\nimport requests\n\n"
        submission = st.text_area("Your assignment code", key=assignment_key, height=360)
        a1,a2 = st.columns(2)
        if a1.button("▶ Run Assignment", type="primary", use_container_width=True, key=f"runassignment_{module['id']}"):
            ok, output = run_student_code(submission)
            st.session_state[f"assignment_output_{module['id']}"] = output
            st.session_state[f"assignment_ok_{module['id']}"] = ok
        evaluate = a2.button("🤖 Evaluate Assignment", use_container_width=True, key=f"eval_{module['id']}")
        output = st.session_state.get(f"assignment_output_{module['id']}", "")
        if output:
            st.markdown("#### Assignment output")
            st.markdown(f'<div class="console">{output}</div>', unsafe_allow_html=True)
        if evaluate:
            if not st.session_state.student_name.strip():
                st.error("Enter your name in the sidebar before evaluation.")
            else:
                ok, current_output = run_student_code(submission)
                if not ok:
                    evaluation = {"score":20,"result":"KEEP PRACTICING","strengths":["You attempted the assignment."],"improvements":["Fix the code so it runs first."],"feedback":current_output}
                else:
                    with st.spinner("Instructor agent is reviewing your API test..."):
                        evaluation = ai_grade(module, submission, current_output)
                st.session_state.assignment_results[module["id"]] = {**evaluation,"module":module["title"],"stage":module["stage"],"submission":submission,"output":current_output,"evaluated_at":datetime.now().isoformat(timespec="seconds")}
                if evaluation["score"] >= PASS_SCORE:
                    st.session_state.completed[module["id"]] = True
                st.rerun()
    else:
        submission = st.text_area("Your assignment response", height=320, key=f"assignment_text_{module['id']}", placeholder="Write test cases, expected results, observations and PASS/FAIL decisions here...")
        evaluate = st.button("🤖 Evaluate Assignment", type="primary", use_container_width=True, key=f"evalmanual_{module['id']}")
        if evaluate:
            if not st.session_state.student_name.strip():
                st.error("Enter your name in the sidebar before evaluation.")
            elif len(submission.strip()) < 40:
                st.error("Add more detail before evaluation.")
            else:
                with st.spinner("Instructor agent is reviewing your API testing work..."):
                    evaluation = ai_grade(module, submission)
                st.session_state.assignment_results[module["id"]] = {**evaluation,"module":module["title"],"stage":module["stage"],"submission":submission,"evaluated_at":datetime.now().isoformat(timespec="seconds")}
                if evaluation["score"] >= PASS_SCORE:
                    st.session_state.completed[module["id"]] = True
                st.rerun()

    saved = st.session_state.assignment_results.get(module["id"])
    if saved:
        st.divider(); st.markdown("### Instructor Evaluation")
        e1,e2 = st.columns(2); e1.metric("Score", f"{saved['score']}%"); e2.metric("Result", saved["result"])
        if saved["score"] >= PASS_SCORE: st.success("✅ Module passed")
        else: st.warning("Keep practicing and submit again.")
        s1,s2 = st.columns(2)
        with s1:
            st.markdown("**Strengths**")
            for item in saved.get("strengths", []): st.write("✅ " + item)
        with s2:
            st.markdown("**Improve next**")
            for item in saved.get("improvements", []): st.write("➡️ " + item)
        st.info(saved.get("feedback", ""))

# ---------- Progress ----------
with progress_tab:
    st.markdown("### Course Progress")
    rows=[]
    for m in MODULES:
        result = st.session_state.assignment_results.get(m["id"], {})
        rows.append({"Module":f"{m['id']} — {m['title']}","Stage":m["stage"],"Minutes":m["minutes"],"Quiz":"Done" if st.session_state.quiz_done.get(m["id"]) else "—","Score":result.get("score","—"),"Status":"PASS" if st.session_state.completed.get(m["id"]) else ("Attempted" if result else "Not started")})
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    total_minutes = sum(m["minutes"] for m in MODULES)
    p1,p2,p3 = st.columns(3)
    p1.metric("Course Modules", len(MODULES)); p2.metric("Guided Content", f"{round(total_minutes/60,1)} hrs"); p3.metric("Modules Passed", sum(1 for v in st.session_state.completed.values() if v))
    report={"student_name":st.session_state.student_name,"student_id":st.session_state.student_id,"generated_at":datetime.now().isoformat(timespec="seconds"),"modules_passed":sum(1 for v in st.session_state.completed.values() if v),"total_modules":len(MODULES),"results":st.session_state.assignment_results,"playground_history":st.session_state.playground_history}
    st.download_button("↓ Download Progress Report", json.dumps(report, indent=2).encode(), f"{st.session_state.student_name or 'student'}_api_qa_progress.json", "application/json", use_container_width=True)

st.caption("Training API: DummyJSON. POST/PUT/PATCH/DELETE operations are simulated by DummyJSON and do not permanently change server data. Practice code runner restricts HTTP calls to dummyjson.com. Course progress lives in the current Streamlit session unless downloaded.")
