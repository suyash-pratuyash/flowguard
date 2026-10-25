# FlowGuard

FlowGuard is a reliability layer for workflow automation: it classifies a failure, applies a bounded policy, verifies the result, and records evidence. In this repository, the implemented component is a deterministic FastAPI demo API that simulates the failure modes used in the FlowGuard contract.

Status: Phase 1 FastAPI fault-injection API is implemented and validated locally. The n8n recovery workflow remains a planned/ exported artifact, not a fully executed production workflow.

## What this repo contains

FlowGuard is intentionally scoped to a demo fault-injection service and the governing specification. It is not a universal self-healing platform and does not modify production workflows or execute irreversible actions.

The repository currently includes:

- `spec/` — source of truth for scope, architecture, API contract, acceptance criteria, and runbook
- `app/` — FastAPI application implementing the FlowGuard demo API
- `tests/` — pytest validation covering health, success, rate-limit recovery, service outage, invalid data, and validation edge cases
- `workflows/` — exported n8n recovery workflow JSON for orchestration design
- `scripts/` — manual PowerShell checks for local validation
- `evidence/` — captured verification results and project evidence
- `data/` — local state directory for audit or runtime data

## System intent

The project addresses three common workflow failures:

- Rate limits: a retryable 429 with `Retry-After: 2` and a bounded retry window
- Transient outages: simulated service unavailability returning 503
- Invalid input: payload validation failures that stop the flow and require review

The policy is deliberately conservative:

- only SAFE_READ operations are auto-retryable
- retry count is capped at 2 attempts
- recovery is considered valid only after verified success
- invalid data never triggers invented fields or silent retries

## API contract

The service follows the approved contract in `spec/03-api-contract.md`.

Health check:

- `GET /health` → `200 {"status":"ok","service":"flowguard-demo-api"}`

Target request:

- `POST /api/target`
- Body:

```json
{
  "request_id": "demo-001",
  "scenario": "RATE_LIMIT_ONCE",
  "attempt": 1,
  "payload": {"requiredField": "demo-value"}
}
```

Allowed scenarios:

- `SUCCESS`
- `RATE_LIMIT_ONCE`
- `SERVICE_UNAVAILABLE`
- `INVALID_DATA`

Expected behavior:

- `SUCCESS` → `200 {"status":"ok","request_id":"...","attempt":N}`
- `RATE_LIMIT_ONCE`, attempt 1 → `429 {"error":"RATE_LIMITED","retryable":true,...}` with `Retry-After: 2`
- `RATE_LIMIT_ONCE`, attempt 2+ → `200 {"status":"ok",...}`
- `SERVICE_UNAVAILABLE` → `503 {"error":"SIMULATED_UNAVAILABLE","retryable":true,...}`
- `INVALID_DATA` with missing or blank `requiredField` → `422 {"error":"INVALID_DATA","field":"requiredField","recoverable":false,...}`

## Quick start

### Python setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Run the tests

```powershell
python -m pytest -q
```

### Manual validation checks

A helper script is included for the approved Smoke Test flow:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\manual-checks.ps1
```

The script checks:

- health → `200`
- rate-limit first attempt → `429`
- rate-limit second attempt → `200`
- service unavailable → `503`
- invalid data → `422`

## Repository evidence

This repository includes captured evidence in `evidence/test-results.md`.

Current recorded project result:

- Automated API tests: 9 passed, 1 warning in 1.20s
- Warning: `StarletteDeprecationWarning` from the test client usage of `httpx`
- Manual checks: all expected statuses observed (`200`, `429`, `200`, `503`, `422`)
- Interactive docs: `/docs` loaded successfully

## Project status from spec

The project scope in `spec/00-scope.md` is explicit:

- P0: health endpoint, API target, bounded retry for rate limits, verified success, attempt evidence
- P1: service-unavailable escalation behavior and invalid-data review handling
- P2: AI diagnosis behind a policy gate
- P3: dashboard and richer integrations are out of scope

The current implementation matches the P0/P1 demo contract and the recorded local validation evidence.

## Important guardrails

- The contract in `spec/03-api-contract.md` is frozen for v1.0; field names, scenario names, statuses, and policy behavior are not to be changed casually.
- Recovery is bounded and policy-gated; it is not an unbounded retry loop.
- Safety is prioritized over automation: invalid or unverified states are escalated or reviewed instead of being silently retried.

## Files to review first

- `spec/00-scope.md`
- `spec/03-api-contract.md`
- `app/main.py`
- `tests/test_api.py`
- `workflows/flowguard-recovery.json`
- `evidence/test-results.md`

This README is intentionally grounded in the implemented code and the approved specification rather than aspirational claims.
