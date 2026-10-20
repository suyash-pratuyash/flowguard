# 04 - Acceptance Tests
Owner: Member 3 | Actual results go in evidence/test-results.md. "Passed" = condition visibly verified.

| ID | Setup | Expected | Evidence file | Pri | Actual |
|---|---|---|---|---|---|
| AT-01 Normal success | scenario=SUCCESS, attempt=1 | 200, verified, no retry | AT-01-success.png | P0 | NOT RUN |
| AT-02 429 then success | RATE_LIMIT_ONCE, same request_id, attempt 1 then 2 | 429 + Retry-After 2; Wait; 200; max attempts 2; verified=true; RECOVERED | AT-02-rate-limit-recovery.png + execution data | P0 | NOT RUN |
| AT-03 Persistent 503 | SERVICE_UNAVAILABLE | At most 2 attempts; no loop; ESCALATED | AT-03-503-escalation.png | P1 | NOT RUN |
| AT-04 Invalid data | INVALID_DATA, payload={} | 422; no retry; NEEDS_REVIEW; no side effect | AT-04-invalid-data.png | P1 | NOT RUN |
| AT-05 Invalid AI JSON | Force bad AI fields (only if AI wired) | Reject; no policy bypass; fallback/review logged | AT-05-invalid-ai.png | P2 | NOT RUN |
| AT-06 LLM unavailable | Disable credentials/network (only if AI wired) | Deterministic path still safe | AT-06-llm-fallback.png | P2 | NOT RUN |
| AT-07 Clean reset | Reset, rerun AT-02 | No stale attempts/events | AT-07-reset.md | P1 | NOT RUN |
| AT-08 Fresh terminal | Follow README in new shell | API starts; calls work without IDE state | AT-08-fresh-start.md | P0 | NOT RUN |

Reportable metrics only from real runs: runs passed/total with sample size, retry counts vs cap,
mean recovery time (only if timestamps recorded). Anything else: "not measured".
