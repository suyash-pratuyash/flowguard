# 00 - Scope
Status: APPROVED v1.0 (lead sign-off recorded in spec/SIGNOFF.md on 2026-10-20)

## Working model
The team works as one. One approver (project lead) signs off on decisions. Roles (n8n / API / spec-QA) are
focus areas only, not approval gates. One branch (`main`) unless a conflict actually appears.

## Problem (2-3 sentences)
Automated workflows fail from rate limits, transient outages and bad data. Teams find out late
and diagnose manually, and blind retries can waste quota or repeat side effects.

## Target user
Small teams and builders running business-critical n8n automations.

## Solution
A reliability layer: capture failure -> classify (deterministic) -> policy gate -> bounded
action (retry / stop / escalate) -> verify -> audit. AI may recommend later; policy authorizes.

## One-sentence USP
Not a retry script: failure-class-aware, bounded, policy-gated, verified and auditable recovery.

## Priorities
| Priority | Capability |
|---|---|
| P0 | /health, /api/target, RATE_LIMIT_ONCE, bounded wait/retry, verified success, attempt evidence |
| P1 | SERVICE_UNAVAILABLE -> ESCALATED at cap; INVALID_DATA -> NEEDS_REVIEW (no retry) |
| P2 | LLM structured diagnosis behind policy gate (only after P0/P1 stable) |
| P3 | Dashboard, notifications, extra integrations (out of sprint scope) |

## Explicitly out of scope
Universal self-healing; modifying/deleting production workflows; payments or irreversible
actions; multi-agent, Kubernetes, custom n8n nodes, fine-tuning; production-reliability claims;
invented metrics or mentor feedback.

## Implementation status (update from evidence only)
| Component | Label |
|---|---|
| FastAPI fault-injection API | implemented (automated tests, five manual checks and /docs verified locally on 2026-10-20) |
| n8n recovery workflow | planned |
| Policy gate (n8n IF/Switch) | planned |
| Audit log (JSONL) | planned |
| LLM diagnosis | implemented (spec/06-ai-diagnosis.md, policy gate allowlist and AT-05/AT-06 verified on 2026-10-21) |
| Dashboard / UI | planned (optional) |
