# 03 - API Contract (FROZEN on sign-off)
Approver: project lead (single sign-off) | Version: v1.0 | Status: DRAFT until SIGNOFF.md is complete

Any change to fields, scenario names, outputs or safety rules needs the project lead's approval
and one reviewed commit updating this file and every caller.

## Endpoints
| Method / path | Purpose |
|---|---|
| GET /health | Readiness. 200 `{"status":"ok","service":"flowguard-demo-api"}` |
| POST /api/target | Run a deterministic scenario |
| POST /api/reset (optional, LOCAL ONLY) | Clear demo state; disabled on any public deployment |
| POST /api/auditevents, GET /api/auditevents (optional) | Only if audit is served by FastAPI |

## Canonical request (POST /api/target)
```json
{
  "request_id": "demo-001",
  "scenario": "RATE_LIMIT_ONCE",
  "attempt": 1,
  "payload": {"requiredField": "demo-value"}
}
```
- scenario: `SUCCESS | RATE_LIMIT_ONCE | SERVICE_UNAVAILABLE | INVALID_DATA`
- request_id: 1-80 chars; IDENTICAL across attempts of one recovery event
- attempt: integer 1-5 accepted by API; the ORCHESTRATOR caps at 2 and increments explicitly
- payload: object; operation is a safe read, no external side effects

## Responses
| scenario | attempt | HTTP | Body / header |
|---|---|---|---|
| SUCCESS | any | 200 | `{"status":"ok","request_id":"...","attempt":N}` |
| RATE_LIMIT_ONCE | 1 | 429 | `{"error":"RATE_LIMITED","retryable":true,"request_id":"...","attempt":1}` + header `Retry-After: 2` |
| RATE_LIMIT_ONCE | 2+ | 200 | `{"status":"ok","request_id":"...","attempt":2}` |
| SERVICE_UNAVAILABLE | any | 503 | `{"error":"SIMULATED_UNAVAILABLE","retryable":true,"request_id":"...","attempt":N}` |
| INVALID_DATA | any, requiredField missing/blank/non-string | 422 | `{"error":"INVALID_DATA","field":"requiredField","recoverable":false,"request_id":"...","attempt":N}` |
| INVALID_DATA | any, requiredField valid | 200 | `{"status":"ok","request_id":"...","attempt":N}` |
| (unknown scenario) | any | 422 | FastAPI/Pydantic validation error (Literal enforces the list) |

## Error taxonomy and terminal states
| Category | Rule | Terminal status |
|---|---|---|
| RATE_LIMIT | HTTP 429, respect Retry-After | RECOVERED if verified; ESCALATED if cap reached |
| TRANSIENT | 502/503/504 or recognized timeout | ESCALATED after budget |
| INVALID_DATA | 400/422 | NEEDS_REVIEW (never invent fields) |
| AUTH / PERMISSION | 401/403 | STOPPED / NEEDS_REVIEW, no retry |
| NOT_FOUND / CONFLICT | 404/409 | Stop |
| LLM_INVALID (P2) | Bad JSON, unknown enum, low confidence | SAFE_FALLBACK or NEEDS_REVIEW |

Terminal states: `SUCCESS, RECOVERED, ESCALATED, NEEDS_REVIEW, STOPPED, SAFE_FALLBACK`.
Safety invariant: "recovery attempted" is NOT "recovery verified".

## Policy table (single source of truth)
| Condition | Action |
|---|---|
| status 429 AND operation SAFE_READ AND attempt < 2 | WAIT_AND_RETRY, wait = max(2, Retry-After) |
| status 502/503/504 AND SAFE_READ AND attempt < 2 | RETRY_ONCE |
| status 400/401/403/404/409/422 | STOP_AND_REVIEW |
| anything else, or cap reached | STOP_OR_ESCALATE |

Max attempts = 2. Only SAFE_READ is auto-retryable. Never an unbounded loop.

## Audit event (JSONL, one object per line) - PROPOSED, needs approval
```json
{"event_id":"evt-001","incident_id":"demo-001","event_type":"ATTEMPT_FAILED",
 "timestamp":"2026-10-20T10:00:00Z",
 "details":{"scenario":"RATE_LIMIT_ONCE","attempt":1,"status":429,"category":"RATE_LIMIT","action":"WAIT_AND_RETRY"}}
```
event_type values: `INCIDENT_OPENED, ATTEMPT_FAILED, POLICY_DECISION, ATTEMPT_SUCCEEDED, VERIFIED, TERMINAL`.
details must be redacted: no secrets, no full payloads.

## Manual checks (PowerShell)
See Playbook section 5; expected statuses: health 200; RATE_LIMIT_ONCE a1 429, a2 200;
SERVICE_UNAVAILABLE 503; INVALID_DATA with empty payload 422.
