# 06 - Hackathon Pitch: Speaker-Notes Script

Owners: Member 1 + Member 3 | Status: DRAFT v1.0
Matches the 2-minute narration in `spec/05-demo-runbook.md`.

## How to use this
- Target length: **2:00**. Each block below has a time window, a one-line GOAL, and
  word-for-word NARRATION you can read or paraphrase.
- **ACTION** = what you do on screen while talking. **SAFETY** = the honesty rule to obey.
- If n8n fails live, say the fallback line verbatim (see §Fallback). Never imply n8n ran it.

---

## Pre-demo checklist (do this before you present, not on the clock)
- FastAPI running; `GET /health` returns `200 {"status":"ok"}`.
- n8n workflow open; HTTP URL matches the network context (localhost vs host.docker.internal).
- Fresh `request_id` (e.g. `demo-001`); audit log cleared via safe local reset.
- Tabs with secrets closed; backup recording/screenshots ready in case live fails.

---

## 0:00–0:20 — Problem + architecture
GOAL: Make them feel the pain, then name the pipeline.

NARRATION:
> "Automated workflows fail all the time — rate limits, transient outages, bad data. The
> usual 'fix' is a blind retry loop that burns API quota or repeats side effects, and the
> team finds out hours later. FlowGuard is a reliability layer that treats a retry as a
> *decision*, not a reflex: capture the failure, classify it, check a policy, take a bounded
> action, verify the result, and record it."

ACTION: Show the one architecture slide: Capture → Classify → Policy Gate → Bounded Action → Verify → Audit.
SAFETY: Don't claim universal self-healing. It's a bounded, policy-gated recovery pattern.

---

## 0:20–0:45 — Trigger RATE_LIMIT_ONCE; first response 429
GOAL: Show a real, deterministic failure we can reason about.

NARRATION:
> "I'll trigger the rate-limit scenario. First attempt comes back `429 RATE_LIMITED`, and
> notice the service hands us a `Retry-After: 2` header. That's the signal we respect instead
> of hammering the endpoint."

ACTION: Fire `RATE_LIMIT_ONCE` with `attempt=1`. Point to the `429` status and the `Retry-After: 2` header.
SAFETY: This is a deterministic fault-injection API — no external outage is needed to reproduce it.

---

## 0:45–1:10 — Classification, policy allow, Wait=2s, attempt=2
GOAL: Show the decision logic — the part that makes this not a retry script.

NARRATION:
> "FlowGuard classifies that `429` as a RATE_LIMIT. Then the policy gate checks three things:
> is this a SAFE_READ operation, are we under the attempt cap of two, and is the status
> actually retryable? All yes — so it waits the two seconds and makes attempt two. If any of
> those were false, it would stop, not retry."

ACTION: Walk the classify node → policy/IF node → Wait node → second HTTP call with `attempt=2`.
SAFETY: Emphasize the cap (max 2) and SAFE_READ-only — this is what prevents infinite loops and unsafe actions.

---

## 1:10–1:30 — Attempt 2 returns 200; verify body + request_id
GOAL: Prove recovery is *verified*, not assumed.

NARRATION:
> "Attempt two returns `200`. But we don't declare victory on a status code alone — we verify
> the body says `status: ok` and the `request_id` matches the one we sent. Only then is this
> marked RECOVERED."

ACTION: Show the `200` response, highlight `status:"ok"` and the matching `request_id`.
SAFETY: "Verified success" is a specific check, not an assumption — say so.

---

## 1:30–1:50 — Audit record; optionally 503 or malformed case
GOAL: Show the evidence trail and the "refuse to retry" case.

NARRATION:
> "Every run leaves an audit record: the original failure, the action taken, the attempts, and
> the final state. And the safety story cuts both ways — if I send invalid data, FlowGuard
> returns `422` and *stops*. It escalates for human review instead of inventing fields or
> silently retrying. A transient `503` behaves the same way: retry to the cap, then escalate."

ACTION: Show the audit entry. If time allows, fire `INVALID_DATA` (→ `422`, stops) or `SERVICE_UNAVAILABLE` (→ `503`, escalates).
SAFETY: Bad data never triggers invented fields or silent retries — this is the headline guardrail.

---

## 1:50–2:00 — Implemented vs. next
GOAL: Close with honest scope and credibility.

NARRATION:
> "Built and validated today: the FastAPI reliability contract, the policy semantics, and the
> evidence — nine automated tests passing and five manual checks confirming the exact status
> codes. Next is wiring the n8n orchestration end-to-end and adding an LLM that *recommends* a
> diagnosis — but never authorizes an action. Policy always holds the pen. That's FlowGuard:
> failure-aware, bounded, verified, auditable recovery."

ACTION: Show the "built vs. next" slide.
SAFETY: Be explicit that n8n orchestration and LLM diagnosis are planned, not fully executed.

---

## Fallback (if live n8n breaks)
Say verbatim:
> "n8n isn't cooperating live, so I'll show the same contract through our local fallback
> harness — this is the Python path, not n8n running the flow."
Then run the pytest suite or `scripts/manual-checks.ps1` to show the same `200 → 429 → 200 → 503 → 422` sequence.
NEVER imply n8n executed the run when it was the local harness.

---

## Quick reference — expected demo outputs
| Step | Call | Expected |
|---|---|---|
| Health | `GET /health` | `200 {"status":"ok","service":"flowguard-demo-api"}` |
| Rate limit, attempt 1 | `POST /api/target` `RATE_LIMIT_ONCE` | `429 RATE_LIMITED`, `Retry-After: 2` |
| Rate limit, attempt 2 | `POST /api/target` `RATE_LIMIT_ONCE` | `200 {"status":"ok"}` |
| Outage | `POST /api/target` `SERVICE_UNAVAILABLE` | `503 SIMULATED_UNAVAILABLE` → escalate at cap |
| Invalid data | `POST /api/target` `INVALID_DATA` (blank field) | `422 INVALID_DATA`, stop for review |
