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
from course_path import show_course_path
from chapter_content import show_chapter
from chapter_walkthroughs import render_detail
from assignment_help import hints_for, solution_for, explanation_for
from assignment_review import review_automation

st.set_page_config(page_title="API QA Academy", page_icon="🔌", layout="wide")
MODEL = st.secrets.get("OPENAI_MODEL", "gpt-5.4-nano")
PASS_SCORE = 70
MODULES = expanded_modules()

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 0% 0%,rgba(37,99,235,.10),transparent 28%),radial-gradient(circle at 100% 0%,rgba(14,165,233,.10),transparent 25%),#f8fafc}
.block-container{max-width:1280px;padding-top:1.2rem;padding-bottom:3rem}.hero{background:linear-gradient(135deg,#0f172a,#172554 52%,#0c4a6e);padding:26px 30px;border-radius:24px;color:white;box-shadow:0 18px 45px rgba(15,23,42,.18);margin-bottom:16px}.hero h1{margin:0;font-size:31px}.hero p{color:#cbd5e1}.chips{display:flex;gap:8px;flex-wrap:wrap}.chip{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);padding:6px 10px;border-radius:999px;font-size:12px;font-weight:700}.stage{font-size:12px;font-weight:850;text-transform:uppercase;letter-spacing:.08em;color:#2563eb}.lesson-title{font-size:25px;font-weight:850;color:#0f172a}.subtle{color:#64748b}.card{background:white;border:1px solid #e2e8f0;border-radius:16px;padding:16px 18px;box-shadow:0 4px 16px rgba(15,23,42,.04);margin:8px 0 14px}.mental{background:#eff6ff;border-left:4px solid #2563eb;border-radius:12px;padding:13px 15px;margin:10px 0}.flow,.console{background:#0f172a;color:#dbeafe;padding:14px 16px;border-radius:14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap}.console{background:#020617;color:#e2e8f0;max-height:430px;overflow:auto}.method{display:inline-block;padding:4px 9px;border-radius:8px;background:#dbeafe;color:#1d4ed8;font-size:12px;font-weight:850;margin-right:6px}div[data-testid="stMetric"]{background:white;border:1px solid #e2e8f0;border-radius:15px;padding:12px 14px}.stTabs [data-baseweb="tab-list"]{gap:7px;background:#eaf0f7;padding:6px;border-radius:14px}.stTabs [data-baseweb="tab"]{border-radius:10px;height:42px;font-weight:750}.stButton>button,.stDownloadButton>button{border-radius:12px;font-weight:750}div[data-testid="stTextArea"] textarea{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;border-radius:12px!important}footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)


def is_dummyjson_url(url):
    try:
        p = urlparse(url)
        return p.scheme == "https" and p.hostname == "dummyjson.com"
    except Exception:
        return False


def full_url(path):
    path = (path or "").strip()
    if path.startswith("https://"):
        return path
    return BASE_URL + (path if path.startswith("/") else "/" + path)


def send_api(method, path, headers=None, body=None):
    url = full_url(path)
    if not is_dummyjson_url(url):
        raise ValueError("Only https://dummyjson.com endpoints are allowed in this classroom.")
    started = time.perf_counter()
    r = requests.request(method.upper(), url, headers=headers or {}, json=body if method.upper() in {"POST","PUT","PATCH"} else None, timeout=10)
    elapsed = round((time.perf_counter() - started) * 1000)
    try:
        data = r.json()
    except Exception:
        data = r.text
    return r, data, elapsed


def sample_code(m):
    url = BASE_URL + m["path"]
    if m["id"] == "26":
        return 'import requests\n\npayload = {"username":"emilys","password":"emilyspass"}\nresponse = requests.post("https://dummyjson.com/auth/login", json=payload, timeout=10)\nprint(response.status_code)\nprint("accessToken" in response.json())'
    if m["id"] == "27":
        return 'import requests\n\nlogin = requests.post("https://dummyjson.com/auth/login", json={"username":"emilys","password":"emilyspass"}, timeout=10)\ntoken = login.json()["accessToken"]\nheaders = {"Authorization": f"Bearer {token}"}\nresponse = requests.get("https://dummyjson.com/auth/me", headers=headers, timeout=10)\nprint(response.status_code)\nprint(response.json()["username"])'
    if m["method"] == "POST":
        return f'import requests\n\npayload = {{"firstName":"Alex","age":30}}\nresponse = requests.post("{url}", json=payload, timeout=10)\nprint(response.status_code)\nprint(response.json())'
    if m["method"] in {"PUT","PATCH"}:
        return f'import requests\n\npayload = {{"lastName":"Automation"}}\nresponse = requests.{m["method"].lower()}("{url}", json=payload, timeout=10)\nprint(response.status_code)\nprint(response.json())'
    if m["method"] == "DELETE":
        return f'import requests\n\nresponse = requests.delete("{url}", timeout=10)\nprint(response.status_code)\nprint(response.json())'
    return f'import requests\n\nresponse = requests.get("{url}", timeout=10)\nprint(response.status_code)\ndata = response.json()\nprint(data)'


class SafeRequests:
    @staticmethod
    def check(url):
        if not is_dummyjson_url(url):
            raise ValueError("Only dummyjson.com is allowed.")
    @classmethod
    def get(cls, url, **kwargs): cls.check(url); kwargs.setdefault("timeout",10); return requests.get(url, **kwargs)
    @classmethod
    def post(cls, url, **kwargs): cls.check(url); kwargs.setdefault("timeout",10); return requests.post(url, **kwargs)
    @classmethod
    def put(cls, url, **kwargs): cls.check(url); kwargs.setdefault("timeout",10); return requests.put(url, **kwargs)
    @classmethod
    def patch(cls, url, **kwargs): cls.check(url); kwargs.setdefault("timeout",10); return requests.patch(url, **kwargs)
    @classmethod
    def delete(cls, url, **kwargs): cls.check(url); kwargs.setdefault("timeout",10); return requests.delete(url, **kwargs)


SAFE_REQUESTS = SimpleNamespace(get=SafeRequests.get,post=SafeRequests.post,put=SafeRequests.put,patch=SafeRequests.patch,delete=SafeRequests.delete)
ALLOWED_BUILTINS = {"print":print,"len":len,"str":str,"int":int,"float":float,"bool":bool,"dict":dict,"list":list,"range":range,"type":type,"isinstance":isinstance,"sum":sum,"min":min,"max":max,"abs":abs}


def safe_import(name, *args, **kwargs):
    if name == "requests":
        return SAFE_REQUESTS
    raise ImportError("Only requests is available in the practice runner.")


def run_student_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"Syntax error line {exc.lineno}: {exc.msg}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(a.name != "requests" for a in node.names):
            return False, "Only import requests is allowed."
        if isinstance(node, ast.ImportFrom):
            return False, "Use import requests."
        if isinstance(node, (ast.ClassDef, ast.With, ast.AsyncWith, ast.AsyncFunctionDef, ast.Await, ast.Yield, ast.YieldFrom, ast.Global, ast.Nonlocal, ast.Delete)):
            return False, f"{type(node).__name__} is not needed in this runner."
        if isinstance(node, ast.Name) and node.id in {"eval","exec","open","compile","globals","locals","input","help","dir","getattr","setattr","delattr","breakpoint"}:
            return False, f"{node.id} is not allowed."
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return False, "Special attributes are not allowed."
    builtins = dict(ALLOWED_BUILTINS)
    builtins["__import__"] = safe_import
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            namespace = {"__builtins__": builtins}
            exec(compile(code, "<student_code>", "exec"), namespace, namespace)
            for name, obj in list(namespace.items()):
                if name.startswith("test_") and callable(obj):
                    obj()
                    print(f"PASS: {name}")
        text = out.getvalue().rstrip()
        return True, text[:8000] or "(Code ran successfully. No printed output.)"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def local_grade(m, submission, output=""):
    text = (submission + "\n" + output).lower()
    score = 35
    strengths, improvements = [], []
    if len(submission.strip()) > 80:
        score += 15; strengths.append("Meaningful attempt with enough detail.")
    if any(x in text for x in ["status","status_code","200","404"]):
        score += 15; strengths.append("You considered HTTP status behavior.")
    if any(x in text for x in ["json","response","assert","expected"]):
        score += 20; strengths.append("You included response or validation thinking.")
    if m["stage"] in {"API Automation","Advanced Automation"} and "assert" not in text:
        improvements.append("Add explicit assertions so the test can decide PASS/FAIL.")
    else:
        score += 10
    if not improvements:
        improvements.append("Add one more negative or edge check for stronger coverage.")
    score = min(score, 100)
    return {"score":score,"result":"PASS" if score>=PASS_SCORE else "KEEP PRACTICING","strengths":strengths or ["You attempted the assignment."],"improvements":improvements,"feedback":"Local grading checked API concepts, expected-vs-actual thinking and validation quality."}


def ai_grade(m, submission, output=""):
    key = st.secrets.get("OPENAI_API_KEY")
    if not key:
        return local_grade(m, submission, output)
    prompt = f'''You are a patient senior API QA automation instructor.
Grade only this module.
MODULE: {m['id']} - {m['title']}
STAGE: {m['stage']}
GOAL: {m['goal']}
ASSIGNMENT: {m['assignment']}
STUDENT SUBMISSION:\n{submission}
OUTPUT:\n{output}
Score: concept correctness 25, test design/coverage 25, expected-vs-actual validation 20, implementation quality 20, clarity 10.
For automation modules, penalize code that only prints and has no meaningful assertions when assertions are expected.
Return ONLY JSON: {{"score":0,"result":"PASS","strengths":["..."],"improvements":["..."],"feedback":"2-4 beginner-friendly sentences"}}. 70+ is PASS.'''
    try:
        raw = OpenAI(api_key=key).responses.create(model=MODEL, input=prompt).output_text.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(raw)
        data["score"] = max(0,min(100,int(data.get("score",0))))
        data["result"] = "PASS" if data["score"]>=PASS_SCORE else "KEEP PRACTICING"
        return data
    except Exception:
        return local_grade(m, submission, output)


def quiz_for(m):
    t = m["title"].lower()
    if "auth" in t or "bearer" in t: return ("What follows Bearer in an Authorization header?",["Access token","Status code","URL","JSON key"],"Access token")
    if "json" in t: return ("A JSON object usually becomes what in Python?",["dict","int","HTTP code","tuple only"],"dict")
    if "query" in t or "path" in t: return ("Which is a query parameter?",["?limit=5","/users/5","200","Bearer"],"?limit=5")
    if "pytest" in t: return ("What prefix does pytest commonly discover?",["test_","run_","qa_","case_"],"test_")
    return ("What should QA compare?",["Expected vs actual","Only screenshots","Only URLs","Only code length"],"Expected vs actual")


for key, default in {"student_name":"","student_id":"","completed":{},"quiz_done":{},"assignment_results":{},"playground_history":[]}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown('''<div class="hero"><h1>🔌 API QA Academy</h1><p>From zero API knowledge → manual API testing → Python automation → pytest framework.</p><div class="chips"><span class="chip">36 guided modules</span><span class="chip">🌐 Live API Lab</span><span class="chip">🐍 Python practice</span><span class="chip">🔐 Authentication</span><span class="chip">🤖 AI evaluation</span></div></div>''', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎓 Student")
    st.session_state.student_name = st.text_input("Name", value=st.session_state.student_name)
    st.session_state.student_id = st.text_input("Student ID / Email", value=st.session_state.student_id)
    st.divider(); st.markdown("### 🧭 Learning Path")
    st.caption("Select a module: its lesson appears first in 📘 Learn This Chapter. The previous always-visible overview has been removed.")
    selected_stage = st.selectbox("Stage", STAGES)
    stage_modules = [m for m in MODULES if m["stage"] == selected_stage]
    labels = [f"{m['id']}. {m['title']} · {m['minutes']} min" for m in stage_modules]
    selected_label = st.radio("Module", labels, label_visibility="collapsed")
    module = stage_modules[labels.index(selected_label)]
    passed = sum(1 for m in MODULES if st.session_state.completed.get(m["id"]))
    st.progress(passed/len(MODULES), text=f"Course progress: {passed}/{len(MODULES)} passed")

m1,m2,m3,m4 = st.columns(4)
m1.metric("Module", f"{module['id']} / {len(MODULES)}")
m2.metric("Stage", STAGES.index(module["stage"])+1)
m3.metric("Estimated", f"{module['minutes']} min")
m4.metric("Passed", sum(1 for v in st.session_state.completed.values() if v))
st.markdown(f'<div class="stage">{module["stage"]}</div><div class="lesson-title">Module {module["id"]} — {module["title"]}</div><div class="subtle">Goal: {module["goal"]}</div>', unsafe_allow_html=True)

learn_tab, lab_tab, practice_tab, assignment_tab, progress_tab = st.tabs(["📘 Learn This Chapter","🌐 API Lab","🧪 Practice","📝 Assignment","📊 Progress"])

with learn_tab:
    show_chapter(module)
    render_detail(module)
    st.divider()
    st.markdown("### Additional lesson notes")
    st.markdown(module["learn"])
    st.markdown(f"**Remember:** {module['mental']}")
    st.markdown("### Try the chapter endpoint")
    st.code(f"{module['method']} {BASE_URL}{module['path']}", language="http")
    if module["stage"] in {"API Automation", "Advanced Automation"}:
        st.markdown("### Python example")
        st.code(sample_code(module), language="python")
    st.markdown("Use the API Lab tab to send the request, Practice to try it, and Assignment to submit your work.")

with lab_tab:
    st.markdown("### Live DummyJSON API Playground")
    st.caption("A lightweight Postman-style lab. Only dummyjson.com is allowed.")
    c1,c2 = st.columns([1,3])
    method = c1.selectbox("Method", ["GET","POST","PUT","PATCH","DELETE"], index=["GET","POST","PUT","PATCH","DELETE"].index(module["method"]), key=f"method_{module['id']}")
    path = c2.text_input("Endpoint", value=module["path"], key=f"path_{module['id']}")
    headers_text = st.text_area("Headers (JSON)", value='{"Accept":"application/json"}', height=90, key=f"headers_{module['id']}")
    default_body = '{\n  "firstName": "Alex",\n  "age": 30\n}' if method in {"POST","PUT","PATCH"} else "{}"
    body_text = st.text_area("Request Body (JSON)", value=default_body, height=130, disabled=method not in {"POST","PUT","PATCH"}, key=f"body_{module['id']}")
    if st.button("🚀 Send Request", type="primary", use_container_width=True, key=f"send_{module['id']}"):
        try:
            headers = json.loads(headers_text or "{}")
            body = json.loads(body_text or "{}") if method in {"POST","PUT","PATCH"} else None
            r, data, elapsed = send_api(method, path, headers, body)
            st.session_state[f"lab_{module['id']}"] = {"status":r.status_code,"time":elapsed,"headers":dict(r.headers),"data":data,"url":r.url}
            st.session_state.playground_history.append({"time":datetime.now().isoformat(timespec="seconds"),"method":method,"url":r.url,"status":r.status_code,"ms":elapsed})
        except Exception as exc:
            st.error(f"Request error: {exc}")
    result = st.session_state.get(f"lab_{module['id']}")
    if result:
        r1,r2,r3 = st.columns(3)
        r1.metric("Status", result["status"]); r2.metric("Response Time", f"{result['time']} ms"); r3.metric("Method", method)
        st.markdown("**Response Body**")
        text = json.dumps(result["data"], indent=2, ensure_ascii=False) if isinstance(result["data"], (dict,list)) else str(result["data"])
        st.markdown(f'<div class="console">{text}</div>', unsafe_allow_html=True)
        with st.expander("Response headers"):
            st.json(result["headers"])

with practice_tab:
    if module["stage"] in {"API Foundations","Manual API Testing"}:
        st.markdown("### Guided manual practice")
        st.info(module["assignment"])
        practice = st.text_area("Your observations / checks", height=240, key=f"practice_text_{module['id']}", placeholder="Expected status:\nActual status:\nResponse checks:\nPASS/FAIL:\nAdditional negative test:")
        if st.button("Check My Practice", type="primary", key=f"check_practice_{module['id']}"):
            if len(practice.strip()) < 50:
                st.warning("Add expected result, actual result and at least two response checks.")
            else:
                st.success("✅ Good practice attempt. Now move to the assignment.")
    else:
        st.markdown("### Python API practice")
        if module["stage"] == "Advanced Automation":
            st.info("Run advanced pytest code in VS Code. In-app Run Practice is disabled because it cannot run pytest fixtures or decorators.")
        code_key = f"practice_code_{module['id']}"
        if code_key not in st.session_state:
            st.session_state[code_key] = sample_code(module)
        code = st.text_area("Edit the code", key=code_key, height=340)
        b1,b2 = st.columns(2)
        if b1.button("▶ Run Practice", type="primary", use_container_width=True, key=f"run_practice_{module['id']}", disabled=module["stage"] == "Advanced Automation"):
            ok, output = run_student_code(code)
            st.session_state[f"practice_output_{module['id']}"] = output
            st.session_state[f"practice_ok_{module['id']}"] = ok
        if b2.button("↺ Reset Example", use_container_width=True, key=f"reset_{module['id']}"):
            st.session_state[code_key] = sample_code(module)
            st.rerun()
        output_key = f"practice_output_{module['id']}"
        if output_key in st.session_state:
            if st.session_state.get(f"practice_ok_{module['id']}"):
                st.success("Code ran successfully.")
            else:
                st.error("Fix the error and try again.")
            st.markdown(f'<div class="console">{st.session_state[output_key]}</div>', unsafe_allow_html=True)
        with st.expander("Need a hint?"):
            st.write("Start from the working example. Change one thing at a time. For automation modules, add assertions for status and important JSON values.")

with assignment_tab:
    st.markdown("### Module Assignment")
    st.markdown(f'<div class="card"><b>Task</b><br>{module["assignment"]}</div>', unsafe_allow_html=True)
    if module["stage"] in {"API Automation","Advanced Automation"}:
        if module["stage"] == "Advanced Automation":
            st.warning("Advanced pytest assignments require VS Code and python -m pytest -v. In-app evaluation checks code structure only; it cannot verify a real pytest run.")
        akey = f"assignment_code_{module['id']}"
        if akey not in st.session_state:
            st.session_state[akey] = "# Write your solution here\nimport requests\n\n"
        with st.expander("💡 Need a hint? Reveal one step at a time", expanded=False):
            hint_key = f"assignment_hint_level_{module['id']}"
            if hint_key not in st.session_state:
                st.session_state[hint_key] = 0
            hints = hints_for(module["id"])
            if st.button("Show next hint", key=f"next_hint_{module['id']}", disabled=st.session_state[hint_key] >= len(hints)):
                st.session_state[hint_key] = min(len(hints), st.session_state[hint_key] + 1)
            for hint in hints[:st.session_state[hint_key]]:
                st.info(hint)
            if st.session_state[hint_key] >= len(hints):
                st.caption("All hints revealed. Try writing your code before opening the solution.")
        with st.expander("👀 See reference solution (after you try)", expanded=False):
            st.warning("Learning tip: attempt the assignment first, then compare your approach with this reference.")
            st.code(solution_for(module["id"]), language="python")
            st.caption(explanation_for(module["id"]))
        submission = st.text_area("Your assignment code", key=akey, height=360)
        a1,a2 = st.columns(2)
        if a1.button("▶ Run Assignment", type="primary", use_container_width=True, key=f"run_assignment_{module['id']}", disabled=module["stage"] == "Advanced Automation"):
            ok, output = run_student_code(submission)
            st.session_state[f"assignment_output_{module['id']}"] = output
            st.session_state[f"assignment_ok_{module['id']}"] = ok
            st.session_state[f"assignment_run_source_{module['id']}"] = submission
        evaluate = a2.button("🤖 Evaluate Assignment", use_container_width=True, key=f"eval_{module['id']}")
        output = st.session_state.get(f"assignment_output_{module['id']}", "")
        run_source = st.session_state.get(f"assignment_run_source_{module['id']}")
        if output and run_source == submission:
            if st.session_state.get(f"assignment_ok_{module['id']}"):
                st.info("Execution: code ran without an exception. This does NOT mean the assignment passed. Select Evaluate Assignment to check the required tasks.")
            else:
                st.error("Execution failed. Fix the Python error below.")
            st.code(output, language="text")
        elif output and run_source != submission:
            st.caption("Code changed since the last run. Run Assignment again to see current execution output.")
        if evaluate:
            if not st.session_state.student_name.strip():
                st.error("Enter your name in the sidebar first.")
            else:
                if module["stage"] == "Advanced Automation":
                    ok, current_output = True, "Static inspection only. Run this pytest project in VS Code."
                else:
                    ok, current_output = run_student_code(submission)
                evaluation = review_automation(module, submission, ok, current_output)
                st.session_state[f"assignment_output_{module['id']}"] = current_output
                st.session_state[f"assignment_ok_{module['id']}"] = ok
                st.session_state[f"assignment_run_source_{module['id']}"] = submission
                st.session_state.assignment_results[module["id"]] = {**evaluation,"module":module["title"],"stage":module["stage"],"submission":submission,"output":current_output,"evaluated_at":datetime.now().isoformat(timespec="seconds")}
                st.session_state.completed[module["id"]] = evaluation["result"] == "PASS"
                st.rerun()
    else:
        submission = st.text_area("Your assignment response", height=320, key=f"assignment_text_{module['id']}", placeholder="Test cases, expected result, actual result, PASS/FAIL, defects or observations...")
        if st.button("🤖 Evaluate Assignment", type="primary", use_container_width=True, key=f"eval_manual_{module['id']}"):
            if not st.session_state.student_name.strip():
                st.error("Enter your name in the sidebar first.")
            elif len(submission.strip()) < 40:
                st.error("Add more detail before evaluation.")
            else:
                evaluation = ai_grade(module, submission)
                st.session_state.assignment_results[module["id"]] = {**evaluation,"module":module["title"],"stage":module["stage"],"submission":submission,"evaluated_at":datetime.now().isoformat(timespec="seconds")}
                if evaluation["score"] >= PASS_SCORE:
                    st.session_state.completed[module["id"]] = True
                st.rerun()
    saved = st.session_state.assignment_results.get(module["id"])
    if saved and saved.get("submission") == submission:
        st.divider(); st.markdown("### Instructor Evaluation")
        x1,x2 = st.columns(2); x1.metric("Score", f"{saved['score']}%"); x2.metric("Result", saved["result"])
        if saved.get("result") == "PASS":
            st.success("✅ PASS — the submitted code met the assignment checks.")
        elif saved.get("result") == "NEEDS LOCAL TEST":
            st.warning("🧪 STATIC REVIEW PASSED — not yet a verified PASS. Run python -m pytest -v in VS Code and check the results.")
        else:
            st.error("❌ FAIL — the code may run, but it has not met all assignment requirements. Fix the issues below.")
        if saved.get("issues"):
            st.markdown("#### What failed, why, and how to fix it")
            for i, issue in enumerate(saved["issues"], 1):
                st.markdown(f"**{i}. {issue['title']}**")
                st.write("**Why:** " + issue["why"])
                st.write("**How to fix:** " + issue["fix"])
            with st.expander("See reference code for comparison"):
                st.code(saved.get("reference", ""), language="python")
        if saved.get("grading_method"):
            st.caption("Assessment: " + saved["grading_method"] + ". A PASS is a learning checkpoint, not full end-to-end validation.")
        y1,y2 = st.columns(2)
        with y1:
            st.markdown("**Strengths**")
            for item in saved.get("strengths",[]): st.write("✅ "+item)
        with y2:
            st.markdown("**Improve next**")
            for item in saved.get("improvements",[]): st.write("➡️ "+item)
        st.info(saved.get("feedback",""))

with progress_tab:
    rows=[]
    for m in MODULES:
        result = st.session_state.assignment_results.get(m["id"], {})
        rows.append({"Module":f"{m['id']} — {m['title']}","Stage":m["stage"],"Minutes":m["minutes"],"Quiz":"Done" if st.session_state.quiz_done.get(m["id"]) else "—","Score":result.get("score","—"),"Status":"PASS" if st.session_state.completed.get(m["id"]) else ("Attempted" if result else "Not started")})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    total_minutes = sum(m["minutes"] for m in MODULES)
    p1,p2,p3 = st.columns(3)
    p1.metric("Course Modules",len(MODULES)); p2.metric("Guided Content",f"{round(total_minutes/60,1)} hrs"); p3.metric("Modules Passed",sum(1 for v in st.session_state.completed.values() if v))
    report = {"student_name":st.session_state.student_name,"student_id":st.session_state.student_id,"generated_at":datetime.now().isoformat(timespec="seconds"),"modules_passed":sum(1 for v in st.session_state.completed.values() if v),"total_modules":len(MODULES),"results":st.session_state.assignment_results,"playground_history":st.session_state.playground_history}
    st.download_button("↓ Download Progress Report", json.dumps(report,indent=2).encode(), f"{st.session_state.student_name or 'student'}_api_qa_progress.json", "application/json", use_container_width=True)

st.caption("Training API: DummyJSON. POST/PUT/PATCH/DELETE are simulated and do not permanently change server data. The practice runner restricts HTTP calls to dummyjson.com. Progress is session-based unless downloaded.")
