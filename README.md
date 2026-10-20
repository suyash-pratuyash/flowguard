# FlowGuard

AI-assisted reliability and recovery for n8n workflows. n8n Sponsored Track, Reforged '26.

**Status: Phase 0 approved. Phase 1 (FastAPI target) code written, awaiting local test run.**

FlowGuard detects a known workflow failure, classifies it, enforces a safe bounded
recovery policy, verifies the outcome, and records evidence. It does NOT claim universal
self-healing.

## Run
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
python -m pytest -q
```

## Where things live
- `spec/`      source of truth (scope, requirements, architecture, API contract, tests, runbook)
- `app/`       FastAPI fault-injection API (Phase 1)
- `workflows/` exported n8n workflow JSON (Phase 3; strip credentials first)
- `evidence/`  real screenshots and `test-results.md`
- `data/`      local audit log (git-ignored)

Rule: a feature is done only when its acceptance test passes and evidence is stored.
