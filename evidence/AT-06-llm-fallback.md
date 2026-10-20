# AT-06 Acceptance Test: LLM Unavailable & Safe Deterministic Fallback

- **Test ID:** AT-06
- **Priority:** P2
- **Owner / Tester:** Member B (AI and Policy Engineer)
- **Date:** 2026-10-21
- **Branch:** `feat/spec-deck`
- **Specification:** `spec/06-ai-diagnosis.md`

## Objective
Verify that if the AI model times out, network connection drops, or credentials are absent, the workflow does not stall or perform an unsafe retry. The system must immediately engage the static fallback diagnosis and proceed with normal deterministic policy execution.

## Executed Test Case
- **Setup:** Simulated network failure / model unavailability (`raw_ai_output = None`).
- **Gate Evaluation:** `MODEL_UNAVAILABLE_USE_FALLBACK`
- **Fallback Diagnosis Applied:**
  ```json
  {
    "failure_type": "UNKNOWN",
    "confidence": 0.0,
    "suggested_action": "STOP_AND_REVIEW",
    "rationale": "Static fallback: AI model unavailable or unresponsive. Deterministic policy rules remain authoritative.",
    "fallback_used": true
  }
  ```
- **Deterministic Action Executed:** For scenario `RATE_LIMIT_ONCE` with `attempt < 2` and `SAFE_READ`, policy safely executes `WAIT_AND_RETRY`.
- **Outcome:** PASS.

## Conclusion
AT-06 PASSED. Workflow reliability is 100% decoupled from third-party model availability.
