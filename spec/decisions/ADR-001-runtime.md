# ADR-001: FastAPI as test API, n8n as orchestrator
Status: Proposed | Owner: Member 3

Decision: FastAPI + Pydantic serves the deterministic fault-injection API; n8n is the intended
orchestrator of retry/policy/verification. Reasons: deterministic demo with no real outage,
auto docs at /docs, typed request validation, quick to build in the 2-day sprint.
Consequence: API contract is framework-independent so the orchestrator or host can change
(local -> hosted HTTPS) with only a base-URL change.
