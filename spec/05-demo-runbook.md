# 05 - Demo Runbook: Step-by-Step Execution & Narration

- **Owners:** Member A (n8n owner) + Member B (QA / Submission Lead)
- **Status:** COMPLETE v1.0
- **Timebox:** 2 minutes live execution

---

## 1. Pre-Demo Checklist (Clean Reset)
Before presenting to the panel or recording:
1. **Start FastAPI Backend:**
   ```powershell
   cd d:\PROJECTS\CodeBlooded
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
   ```
2. **Verify API Readiness:**
   - Open `http://127.0.0.1:8000/health` (must return `{"status":"ok","service":"flowguard-demo-api"}`).
3. **Verify n8n Orchestrator:**
   - Confirm workflow `FlowGuard Recovery Loop` is open in n8n (`http://localhost:5678`).
   - Check that HTTP nodes point to `http://127.0.0.1:8000/api/target`.
4. **Use a Fresh Request ID:**
   - Ensure the Input node uses a fresh identifier (e.g. `demo-live-01`, `demo-live-02`).
5. **No Secrets Visible:**
   - Close tabs with API keys, tokens, or environment files.
   - Have backup real execution screenshots in `evidence/` ready in case of local network disruption.

---

## 2. Live 2-Minute Demonstration Flow

| Time (s) | Visual on Screen | Presenter Narration |
| :---: | :--- | :--- |
| **0:00 - 0:20** | Architecture Diagram / Problem Statement | *"Automation failures in enterprise workflows typically fail silently or retry blindly. Blind retries waste API quotas and risk duplicate side-effects. FlowGuard introduces bounded, policy-gated reliability."* |
| **0:20 - 0:45** | Click **Test step** on Trigger -> First HTTP call returns **429** | *"We trigger a simulated external API call under the `RATE_LIMIT_ONCE` scenario. The mock service deterministically returns HTTP 429 with a `Retry-After: 2` header."* |
| **0:45 - 1:10** | n8n routes into the **Policy Gate**, highlights **Wait 2s**, increments `attempt=2` | *"Notice that the workflow does NOT crash. The Policy Gate checks three rules: status is 429, operation is marked `SAFE_READ`, and attempts < 2. It authorizes a 2-second backoff and schedules attempt 2."* |
| **1:10 - 1:30** | Attempt 2 executes -> returns **200 OK** -> **Verification Node** evaluates | *"Attempt 2 succeeds with HTTP 200. FlowGuard enforces our core invariant: 'Attempted is not Verified'. We strictly check that the status is 2xx, body.status is 'ok', and the request ID matches the original incident before declaring recovery."* |
| **1:30 - 1:50** | Final node highlights **`terminal_status = RECOVERED`** and displays Audit Entry | *"The workflow reaches the terminal state: `RECOVERED` with `verified: true`. An auditable event is appended to the audit log. If this were a 422 Invalid Data error, FlowGuard would immediately stop with zero retries."* |
| **1:50 - 2:00** | Controlled AI Diagnosis summary (`spec/06-ai-diagnosis.md`) | *"Behind this deterministic gate, our AI engine provides failure explanations, but cannot bypass policy or trigger unsafe actions. Thank you!"* |

---

## 3. Alternative Scenarios (If Panel Requests Them)

### Scenario A: Service Unavailable (`503`) - Bounded Retry & Cap
- **Input:** `scenario = "SERVICE_UNAVAILABLE"`
- **Expected Flow:** Attempt 1 (503) &rarr; Policy allows 1 retry &rarr; Attempt 2 (503) &rarr; Attempt cap reached (max 2) &rarr; Routes to `Result: ESCALATED`.
- **Proof:** Exactly two calls made, zero infinite loop.

### Scenario B: Invalid Data (`422`) - Zero Retries
- **Input:** `scenario = "INVALID_DATA"`, `payload = {}`
- **Expected Flow:** Attempt 1 (422) &rarr; Policy detects unrecoverable error &rarr; Immediate halt &rarr; Routes to `Result: NEEDS_REVIEW`.
- **Proof:** Never invents missing data; downstream side-effect node never executed.

---

## 4. Live Fallback Harness
If n8n encounters local port/daemon conflicts during the live session:
```powershell
# Run deterministic API verification in terminal
.\scripts\manual-checks.ps1

# Run AI Policy Gate verification in terminal
.\.venv\Scripts\python.exe .\scripts\test-ai-policy.py
```
*Honesty statement to panel:* *"We are displaying the local fallback harness running against the live FastAPI target service."*
