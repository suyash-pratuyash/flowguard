# 05 - Demo Runbook
Owners: Member 1 + Member 3 | Status: SKELETON (fill commands in Phases 1-3)

## Pre-demo reset
1. Start FastAPI; wait for GET /health = ok
2. Open n8n workflow; confirm HTTP URL fits the network context
3. Fresh request_id (e.g. demo-001); clear audit log via safe local reset
4. Close tabs with secrets; backup recording/screenshots ready (live first)

## 2-minute narration
| Time | Action |
|---|---|
| 0:00-0:20 | Problem + architecture: failure-aware, bounded recovery |
| 0:20-0:45 | Trigger RATE_LIMIT_ONCE; first response 429 |
| 0:45-1:10 | Classification, policy allow, Wait=2s, attempt=2 |
| 1:10-1:30 | Attempt 2 returns 200; verify body + request_id |
| 1:30-1:50 | Audit record; optionally 503 or malformed case |
| 1:50-2:00 | Implemented vs next |

Fallback: if n8n fails, label the Python path "local fallback harness"; never imply n8n ran it.
