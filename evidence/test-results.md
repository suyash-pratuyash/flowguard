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

## Acceptance Tests Verified on Member B Laptop (2026-10-21)

| Test ID | Description | Expected | Actual Result | Status | Evidence File |
|---|---|---|---|---|---|
| **AT-08** | Fresh Terminal Run | Clones & runs without IDE state | Pytest 9 passed; 5 manual checks 200, 429, 200, 503, 422 | **PASS** | `evidence/AT-08-fresh-start.md` |
| **AT-05** | Invalid AI JSON & Disallowed Action | Reject output, safe fallback, enforce policy | Malformed JSON & missing fields rejected; malicious action `BYPASS_AND_DELETE_ALL` blocked | **PASS** | `evidence/AT-05-invalid-ai.md` |
| **AT-06** | LLM Unavailable & Network Down | Deterministic policy remains authoritative | Model down simulation engaged `STATIC_FALLBACK`; bounded retry executed safely | **PASS** | `evidence/AT-06-llm-fallback.md` |

## Notes
- AT-08 verifies complete clean-slate reproducibility.
- AT-05 and AT-06 prove that AI output is safely gated behind deterministic policy checks.
- Workflow-level runs (AT-01 through AT-04) use `workflows/flowguard-recovery.json`.