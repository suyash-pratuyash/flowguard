# AT-05 Acceptance Test: Invalid AI JSON & Field Rejection

- **Test ID:** AT-05
- **Priority:** P2
- **Owner / Tester:** Member B (AI and Policy Engineer)
- **Date:** 2026-10-21
- **Branch:** `feat/spec-deck`
- **Specification:** `spec/06-ai-diagnosis.md`

## Objective
Verify that if an LLM returns malformed JSON, missing fields, out-of-bounds confidence values, or disallowed actions, the Policy Gate rejects the output, logs the incident, engages `SAFE_FALLBACK`, and prevents any unverified action.

## Executed Test Cases

### 1. Malformed / Non-JSON Input
- **Input:** `"Not JSON at all! Error 500"`
- **Gate Evaluation:** `INVALID_JSON_REJECTED`
- **Result:** `SAFE_FALLBACK` engaged (`fallback_used: true`). Deterministic policy (`WAIT_AND_RETRY` for 429) preserved.
- **Outcome:** PASS.

### 2. Missing Required Fields
- **Input:** `{"failure_type": "RATE_LIMIT", "confidence": 0.8}` (missing `suggested_action` and `rationale`)
- **Gate Evaluation:** `MISSING_REQUIRED_FIELDS_REJECTED`
- **Result:** Rejected before execution.
- **Outcome:** PASS.

### 3. Prompt Injection / Malicious Action Attempt
- **Input:** `{"failure_type": "RATE_LIMIT", "confidence": 0.99, "suggested_action": "BYPASS_AND_DELETE_ALL", ...}`
- **Gate Evaluation:** `DISALLOWED_ACTION_REJECTED`
- **Result:** Unsafe action blocked. Deterministic policy rules enforce safe bounded retry only.
- **Outcome:** PASS.

## Conclusion
AT-05 PASSED. Malformed, missing, and hostile model outputs are strictly rejected.
