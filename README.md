# API QA Academy

A beginner-to-advanced Streamlit learning app for API testing and API automation.

## Learning path

1. **API Foundations** — API, client/server, endpoints, request/response, methods, status codes, JSON, headers, parameters, authentication concepts.
2. **Manual API Testing** — GET/POST testing, positive/negative coverage, JSON validation, authentication testing, test-case design.
3. **API Automation** — Python requests, assertions, CRUD automation, headers, query parameters, authentication, bearer tokens, negative automation.
4. **Advanced Automation** — pytest, fixtures, parametrization, reusable API clients, error handling, test data, framework design and a final project.

The course contains **36 guided modules** with Learn, API Lab, Practice, Assignment, AI Evaluation and Progress sections.

## Training API

The app uses `https://dummyjson.com` as its classroom API. POST/PUT/PATCH/DELETE operations are simulated by DummyJSON and do not permanently change server data.

## Features

- W3Schools-style beginner notes and mental models
- Live Postman-style API playground inside Streamlit
- Status code, response time, headers and formatted JSON display
- Python `requests` practice runner restricted to DummyJSON
- Authentication lessons using DummyJSON login/access-token flow
- Manual testing assignments before automation
- AI assignment scoring and feedback
- Local fallback grading when no OpenAI key is configured
- Module progress and downloadable JSON report

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

Deploy with:

- Repository: `mandy1065/API-QA-Academy`
- Branch: `main`
- Main file: `app.py`

Optional Streamlit secrets:

```toml
OPENAI_API_KEY = "YOUR_REAL_OPENAI_API_KEY"
OPENAI_MODEL = "gpt-5.4-nano"
```

Never commit a real API key to GitHub.

## Sample DummyJSON classroom login

The authentication lesson uses DummyJSON's public sample user credentials (`emilys` / `emilyspass`) for training only. Do not use real passwords in course code.
