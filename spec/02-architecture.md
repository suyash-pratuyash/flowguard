# 02 - Architecture
Owners: Member 3 + Member 1 | Status: DRAFT v1.0

## Components and boundaries
| Component | Tech | Owns | Must NOT own |
|---|---|---|---|
| Workflow orchestrator | n8n | Trigger, HTTP calls, status branches, Wait, capped retry, verification, run trace | Unbounded retries; blind execution of LLM suggestions |
| Fault-injection API | FastAPI + Pydantic | Scenario responses, envelope validation, health | Recovery policy; declaring recovery verified |
| Policy gate | n8n IF/Switch + allowlist | Permit retry only for allowed status/operation/attempt | Treating AI output as authorization |
| Audit evidence | JSONL (one store only) + n8n execution history | Incident, attempts, decision, terminal status, timestamps | Secrets, full sensitive payloads |
| LLM diagnosis (P2) | One LLM API | Structured explanation + recommendation | Executing retries, overriding policy |
| Human review | Manual branch | Ambiguous/malformed/unsafe cases | Auto-approve on timeout |

## Data flow
1. Trigger: Manual Trigger sets scenario, request_id, attempt=1, operation=SAFE_READ, max_attempts=2
2. Call: HTTP Request POST /api/target
3. Normalize: keep status code, headers, body
4. Classify: 429 -> RATE_LIMIT; 502/503/504/timeout -> TRANSIENT; 400/422 -> INVALID_DATA
5. Policy gate: retry only if SAFE_READ, attempt < 2, status retryable
6. Execute/stop: 429 -> Wait then attempt=2; repeat 503 -> escalate at cap; 422 -> stop
7. Verify: attempt 2 is 2xx, body status="ok", request_id matches
8. Audit: write original failure, action, attempts, terminal status

## Trust boundary
Untrusted: LLM output, payload contents. Trusted: deterministic policy table and attempt counter.

## Networking
- Same host: http://127.0.0.1:8000/api/target
- n8n in Docker: use host.docker.internal (Docker Desktop) or Compose service name
- Hosted n8n (finale): needs reachable HTTPS FastAPI URL; never expose /api/reset publicly
