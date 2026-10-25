# AT-08 Acceptance Test: Fresh Start & Reproducibility

- **Test ID:** AT-08
- **Priority:** P0
- **Tester / Owner:** Member B
- **Date:** 2026-10-21
- **Branch:** `feat/spec-deck`
- **Environment:** Windows 11, PowerShell, Python 3.13.7

## Objective
Verify that a new teammate / machine can clone the repository, set up the virtual environment, install dependencies, run automated unit tests, launch the FastAPI server, and verify all 5 endpoint responses without relying on any hidden IDE state.

## Step 1: Environment Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
**Outcome:** PASS. Virtual environment created cleanly and all dependencies installed without error.

## Step 2: Automated Tests
```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
**Actual Output:**
```text
.........                                                                [100%]
9 passed, 1 warning in 4.33s
```
**Outcome:** PASS (9 of 9 unit tests passed).

## Step 3: Server Launch & Manual Endpoint Checks
Started API:
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```
Executed verification script:
```powershell
.\scripts\manual-checks.ps1
```
**Actual Output:**
```text
health                       -> 200  {"status":"ok","service":"flowguard-demo-api"}
RATE_LIMIT_ONCE attempt 1    -> 429  Retry-After=2
RATE_LIMIT_ONCE attempt 2    -> 200  {"request_id":"demo-001","attempt":2,"status":"ok"}
SERVICE_UNAVAILABLE attempt 1 -> 503  Retry-After=
INVALID_DATA empty payload   -> 422  Retry-After=
```
**Outcome:** PASS. All 5 endpoints returned expected status codes and payloads.

## Conclusion
AT-08 PASSED. Clean installation and execution verified with zero hidden dependencies.
