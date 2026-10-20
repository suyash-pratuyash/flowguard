# FlowGuard Phase 1 — Test Results

Date: 2026-10-20
Component: FastAPI fault-injection API
Environment: Windows PowerShell, project virtual environment

## Automated tests

Command:
.\.venv\Scripts\python.exe -m pytest -q

Actual result:
9 passed, 1 warning in 1.20s

Warning:
StarletteDeprecationWarning regarding the use of httpx
with starlette.testclient.

## Manual API checks

| Check | Actual result | Outcome |
|---|---|---|
| GET /health | HTTP 200; status=ok | PASS |
| RATE_LIMIT_ONCE, attempt 1 | HTTP 429; Retry-After=2 | PASS |
| RATE_LIMIT_ONCE, attempt 2 | HTTP 200; status=ok | PASS |
| SERVICE_UNAVAILABLE | HTTP 503 | PASS |
| INVALID_DATA, empty payload | HTTP 422 | PASS |

## Interactive documentation

Actual result: Opened http://127.0.0.1:8000/docs successfully.
GET /health and POST /api/target were visible.

Outcome: PASS

## Notes

These results verify the API endpoints, not the complete
n8n recovery workflow. Workflow-level acceptance tests
remain pending until actually executed.