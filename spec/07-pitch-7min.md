# 07 - Hackathon Pitch (7-minute version)
Owners: Member 1 + Member 3 | Status: DRAFT v1.0
Companion to `spec/05-demo-runbook.md` and `spec/06-pitch-script.md`.

## Time budget (7:00 total)
| Window | Beat | Who |
|---|---|---|
| 0:00–0:45 | Hook — the pain | Presenter A |
| 0:45–1:45 | What FlowGuard is + the insight | Presenter A |
| 1:45–3:00 | Architecture walkthrough | Presenter A |
| 3:00–5:30 | Live demo (3 scenarios) | Presenter B drives n8n, A narrates |
| 5:30–6:00 | Evidence + honest scope | A |
| 6:00–6:30 | Deployment / "how do I use this?" | A |
| 6:30–7:00 | Close + ask | A |

Hard rules:
- If anything live fails, say the fallback line in §Fallback and switch to the Python harness.
- Never claim n8n ran a step the Python harness ran.
- No invented metrics. Only read numbers from `evidence/test-results.md`.

---

## 0:00–0:45 — Hook (the pain)
GOAL: Make the room feel the problem in 45 seconds.

NARRATION:
> "Your automation ran at 2 AM. It hit a rate limit, retried fifty times in a loop, burned
> your API quota, and still failed. You found out at 9 AM — from an angry customer. Every
> team running n8n, Zapier, or cron jobs has lived this. Three failures cause almost all of
> it: **rate limits, transient outages, and bad data.** And the usual 'fix' — blind retry —
> often makes it worse by repeating side effects or wasting quota. We built FlowGuard
> because retries shouldn't be reflexes. They should be *decisions*."

ACTION: Title slide → one "pain" slide. Hold eye contact; don't rush.
SAFETY: Keep the pain concrete and plausible. Don't invent a customer story.

---

## 0:45–1:45 — What FlowGuard is + the insight
GOAL: One sentence they'll remember. Then the pipeline.

NARRATION:
> "FlowGuard is a **reliability layer for workflow automation.** It doesn't just retry — it
> classifies the failure, checks a policy, takes a bounded action, verifies the result, and
> leaves an audit trail. The key design principle, especially with AI in the loop, is this:
> **AI may recommend, but policy authorizes.** Even when we add an LLM that diagnoses the
> failure, that LLM never triggers an action on its own. A deterministic policy table does.
> That's the trust boundary that lets you ship this near real systems."

ACTION: Pipeline slide — six boxes: **Capture → Classify → Policy Gate → Bounded Action → Verify → Audit.**
SAFETY: Don't claim "self-healing." The honest words are "failure-aware, bounded, verified, auditable recovery."

---

## 1:45–3:00 — Architecture walkthrough
GOAL: Show the n8n canvas and name the trust boundaries in 75 seconds.

NARRATION:
> "Two components. One: a FastAPI service that deterministically reproduces the three failure
> modes — `429` for rate limit, `503` for outage, `422` for bad data. It's a stand-in for
> *your* real target API: Stripe, HubSpot, an internal service, anything. Two: the n8n
> workflow you're looking at — the orchestrator. It owns the recovery policy; the API does
> not. On the canvas: Manual Trigger initializes the request. HTTP call. **Classify** by
> status code. Then one of three paths: `200` goes through verification. `429` or `503` hit a
> **policy gate** — only SAFE_READ operations, under the attempt cap of two, can retry. `422`
> short-circuits straight to NEEDS_REVIEW — bad data is never retried. There's also an LLM
> diagnosis path running on a local Ollama model, but notice: its output flows into evidence,
> never into the retry decision."

ACTION: Zoom to the n8n canvas. Trace with the cursor: Classify → Policy Gate → Wait → Prepare Attempt 2 → HTTP → Verify. Then point to the LLM subgraph and say "advisory, not authoritative."
SAFETY: Explicitly say the LLM is advisory. If the LLM subgraph isn't wired to run live, say so now, not during the demo.

---

## 3:00–5:30 — Live demo (3 scenarios, ~50s each)

### 3:00–3:50 — Scenario 1: RATE_LIMIT_ONCE → RECOVERED
GOAL: Show the happy-path recovery with verified success.

NARRATION:
> "First scenario: rate limit. I set scenario to `RATE_LIMIT_ONCE`, attempt one, and execute.
> Attempt one comes back `429 RATE_LIMITED` with `Retry-After: 2`. Classify routes to the
> 429 policy gate: SAFE_READ, under cap, retryable — all pass. Wait two seconds. Attempt
> two. We get `200`, and crucially we **verify** the body: `status: ok`, matching
> `request_id`, attempt equals two. Terminal status: **RECOVERED**. Not 'retried' —
> *recovered*."

ACTION: Set `scenario="RATE_LIMIT_ONCE"` in Initialize Request → Execute → walk the trace through the Classify switch (HTTP 429 branch) → Policy Gate (true) → Wait → Attempt 2 → Verify Retry Success → Record Outcome - RECOVERED.
SAFETY: Point explicitly at the `Verify Retry Success` IF node. Verification is the thing that makes this not a retry script.

### 3:50–4:30 — Scenario 2: INVALID_DATA → NEEDS_REVIEW
GOAL: Show the refuse-to-retry case.

NARRATION:
> "Second: bad data. Scenario `INVALID_DATA`, payload with a blank required field. API
> returns `422`. Watch the switch — it bypasses both policy gates entirely and lands on
> **NEEDS_REVIEW**. Zero retries. The reason is recorded. A human is on the hook now, and
> that's the right answer. Blind retry on bad data is how automations create duplicates and
> corrupt records."

ACTION: Change `scenario` to `INVALID_DATA`, set payload `requiredField` to empty string → Execute → point at the `422` output of Classify dropping straight to Record Outcome - NEEDS_REVIEW.
SAFETY: Emphasize "zero retries." This is your strongest safety story.

### 4:30–5:15 — Scenario 3: SERVICE_UNAVAILABLE → ESCALATED (or RECOVERED, be honest)
GOAL: Show bounded retry + the cap behavior.

NARRATION:
> "Third: a transient outage. Scenario `SERVICE_UNAVAILABLE`. First attempt: `503`. Policy
> gate 503: SAFE_READ, under cap, response marks retryable — allowed. Wait, attempt two.
> Our deterministic API returns `503` again. Verification fails. We hit the attempt cap. The
> workflow doesn't loop — it records terminal status **ESCALATED** with a reason. Humans or
> an on-call system take over. The cap is the thing standing between you and a quota fire."

ACTION: `scenario="SERVICE_UNAVAILABLE"` → Execute → trace through 503 policy gate → Wait → Attempt 2 → Verify fails → Record Outcome - ESCALATED.
SAFETY: Say "doesn't loop" out loud. Don't claim the recovery succeeded when it escalated.

### 5:15–5:30 — Audit trail
NARRATION:
> "Every outcome node writes a terminal record: request_id, terminal_status, attempts,
> verified true/false, initial and final HTTP status, action taken. That's your audit trail —
> every decision this workflow made, inspectable after the fact."

ACTION: Click one of the Record Outcome nodes and show the output JSON.

---

## 5:30–6:00 — Evidence + honest scope
GOAL: Earn credibility by naming what's built and what isn't.

NARRATION:
> "What's validated today: the FastAPI contract — **nine automated tests passing**, and five
> manual checks confirming the exact status sequence `200 → 429 → 200 → 503 → 422`. The n8n
> workflow you just saw runs end-to-end on this deterministic target. What's next: wiring the
> LLM diagnosis fully behind the policy gate, and persisting audit records to disk as JSONL
> instead of just the n8n execution history. We're deliberately not claiming universal
> self-healing. We're claiming a *correct, bounded, auditable* recovery pattern."

ACTION: Simple two-column slide: **Built & verified** / **Next**.
SAFETY: Only cite the numbers in `evidence/test-results.md`. Don't round up.

---

## 6:00–6:30 — Deployment / "How does someone use this?"
GOAL: Answer the question judges always ask. Give them a concrete mental model.

See the full Q&A for this in §Judge-Q&A — the "Is this a website?" answer. Short version to say on stage:

NARRATION:
> "Quick note on how this is used, because it's a fair question — FlowGuard isn't a website
> you log into. It's a pattern plus two deployable pieces. The orchestrator is **n8n**,
> which you self-host in Docker or run on n8n Cloud; you import this workflow JSON into your
> n8n instance. The target endpoint in the workflow — right now pointing at our FastAPI
> demo — gets re-pointed at **your real API** in production: Stripe, HubSpot, an internal
> service, anything you want to make resilient. The workflow becomes the reliability wrapper
> between your trigger and that API. For this demo, both pieces are local: FastAPI on
> `localhost:8000`, n8n in Docker reaching it via `host.docker.internal`."

ACTION: One-slide diagram: `[Trigger] → [n8n workflow w/ policy] → [Your real API]`, with "FlowGuard" as the box around n8n.
SAFETY: Don't claim it's production-ready as a hosted service. It's a reference pattern + working orchestrator.

---

## 6:30–7:00 — Close + ask
GOAL: One sticky line + what you want from the judges.

NARRATION:
> "Blind automation is fast until it's catastrophic. FlowGuard makes recovery
> **failure-aware, bounded, verified, and auditable** — the difference between an
> automation that panics at 2 AM and one you can trust. We'd love your feedback on two
> things: whether the policy table is the right abstraction, and where you'd want this
> integrated first. Thank you."

ACTION: Final slide: one-line USP + team names + repo link.

---

## Fallback (if n8n or the demo breaks)
Say verbatim:
> "n8n isn't cooperating live, so I'll run the same contract through our local fallback
> harness. This is the Python path — not n8n running the flow."
Then run:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\manual-checks.ps1
```
or:
```powershell
python -m pytest -q
```
Narrate the `200 → 429 → 200 → 503 → 422` sequence as it prints.

---

## Judge-Q&A — likely questions and crisp answers

### Q: "Is this a website? How does someone actually use it?"
> "No, FlowGuard isn't a hosted website — it's a reliability pattern with two deployable
> parts. The brains live in an **n8n workflow** that you import into your own n8n instance
> (self-hosted in Docker, or n8n Cloud). The workflow calls a target API — in the demo it's
> our FastAPI stub, but in production you'd point it at your real service: Stripe, HubSpot,
> an internal API, whatever's flaky. Your existing triggers — a webhook, a schedule, an
> event — fire the workflow, and it handles the classify-retry-verify-audit cycle before
> handing control back. So the user experience is: 'import JSON, change one URL, done.'"

### Q: "What makes this different from a retry library like Tenacity or Polly?"
> "Three things. One: it's **failure-class-aware** — it treats `429`, `503`, and `422`
> differently, with explicit policies, not a uniform exponential backoff. Two: it's **policy-
> gated** — the operation has to be SAFE_READ and under the attempt cap; irreversible actions
> never auto-retry. Three: it **verifies**, meaning it doesn't declare success on a status
> code — it checks the response body and request correlation. Retry libraries do step one of
> that. FlowGuard does all three plus the audit trail."

### Q: "Where does the LLM fit? Doesn't it make this unsafe?"
> "The LLM only *diagnoses* — it produces a structured recommendation. It never authorizes
> an action. In the workflow it's a parallel path that writes to the audit record. The
> deterministic policy table is what decides retry, stop, or escalate. If the LLM times out
> or returns garbage, the recovery path is unaffected. That's the whole trust-boundary story."

### Q: "What's the max_attempts cap and why is it two?"
> "Two is the demo value from our scope — it's enough to prove the pattern without hiding
> bugs behind many retries. In a real deployment it's a config value per operation class.
> The important property isn't the number; it's that there *is* a cap and that it's
> enforced before the HTTP call, not after."

### Q: "What happens if the LLM is down?"
> "The retry/stop/escalate decision doesn't depend on the LLM. If Ollama is unreachable, the
> diagnosis field is empty, the policy gate still runs, and the outcome is still recorded.
> We validated the policy path independently of the LLM path."

### Q: "How do you handle non-idempotent operations like payments?"
> "We don't — and that's intentional. The policy gate requires `operation: SAFE_READ`
> explicitly. Anything else falls through to escalation. Payments and other irreversible
> actions are out of scope by design; that's in `spec/00-scope.md`."

### Q: "Is this production-ready?"
> "Not as a hosted service, no. The FastAPI contract and the n8n workflow are validated
> locally against the deterministic target. For production, you'd point the workflow at your
> real API, add JSONL persistence for the audit record, and set the max_attempts per
> operation class. The pattern is production-shaped; the deployment story is still a sprint
> of work."

---

## Pre-demo checklist (off the clock)
- [ ] FastAPI running; `GET /health` returns `200`
- [ ] n8n open, workflow loaded, HTTP URL = `http://host.docker.internal:8000/api/target`
- [ ] Fresh `request_id` (e.g. `demo-001`)
- [ ] Ollama up if demoing LLM path; otherwise collapse that subgraph on screen
- [ ] Backup recording of all three scenarios ready
- [ ] Secrets tabs closed
- [ ] Terminal sized readable from the back row

## Quick reference — expected demo outputs
| Step | Call | Expected |
|---|---|---|
| Health | `GET /health` | `200 {"status":"ok","service":"flowguard-demo-api"}` |
| Rate limit, attempt 1 | `POST /api/target` `RATE_LIMIT_ONCE` | `429 RATE_LIMITED`, `Retry-After: 2` |
| Rate limit, attempt 2 | `POST /api/target` `RATE_LIMIT_ONCE` | `200 {"status":"ok"}` |
| Outage | `POST /api/target` `SERVICE_UNAVAILABLE` | `503 SIMULATED_UNAVAILABLE` → escalate at cap |
| Invalid data | `POST /api/target` `INVALID_DATA` (blank field) | `422 INVALID_DATA`, stop for review |
