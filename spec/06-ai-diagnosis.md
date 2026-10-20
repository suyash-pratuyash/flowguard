# 06 - Controlled AI Diagnosis & Policy Gate (Phase 8 Specification)

- **Owner:** Member B (AI and Policy Engineer)
- **Status:** APPROVED v1.0
- **Priority:** P2 (Built behind deterministic policy gate)
- **Safety Rule:** "AI recommends, policy authorizes." The LLM can never authorize or execute any action.

---

## 1. Objective
Add structured AI failure explanation and diagnosis behind the deterministic policy gate. Prove that bad, hallucinated, or missing AI output cannot cause an unsafe action or bypass the retry cap.

---

## 2. Redacted Context Sent to LLM
To preserve security and prevent prompt injection, **no raw payloads, auth tokens, secrets, or customer data** are ever sent to the model.

Only the following 5 sanitized fields are sent:
```json
{
  "scenario": "RATE_LIMIT_ONCE",
  "status_code": 429,
  "error_code": "RATE_LIMITED",
  "attempt": 1,
  "operation": "SAFE_READ"
}
```

---

## 3. System Prompt for LLM
```text
You are FlowGuard AI Diagnosis Engine for automated workflow failures.
Analyze the provided failure context and return a structured JSON assessment.

You MUST respond with valid JSON ONLY. Do not include markdown code blocks, conversational text, or any formatting outside the JSON object.

Allowed failure_type values:
- "RATE_LIMIT"
- "TRANSIENT"
- "INVALID_DATA"
- "AUTH"
- "UNKNOWN"

Allowed suggested_action values:
- "WAIT_AND_RETRY"
- "RETRY_ONCE"
- "STOP_AND_REVIEW"
- "ESCALATE"

Your response must strictly match this JSON schema:
{
  "failure_type": "<one of the allowed failure_type values>",
  "confidence": <float between 0.0 and 1.0>,
  "suggested_action": "<one of the allowed suggested_action values>",
  "rationale": "<1 or 2 concise explanatory sentences>"
}
```

---

## 4. Output JSON Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["failure_type", "confidence", "suggested_action", "rationale"],
  "properties": {
    "failure_type": {
      "type": "string",
      "enum": ["RATE_LIMIT", "TRANSIENT", "INVALID_DATA", "AUTH", "UNKNOWN"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "suggested_action": {
      "type": "string",
      "enum": ["WAIT_AND_RETRY", "RETRY_ONCE", "STOP_AND_REVIEW", "ESCALATE"]
    },
    "rationale": {
      "type": "string",
      "maxLength": 300
    }
  },
  "additionalProperties": false
}
```

---

## 5. Policy Gate Decision Matrix

The Policy Gate sits **between** the AI output and the workflow executor. It evaluates the AI response against the deterministic truth:

| AI Output Condition | Gate Action | Resulting Workflow State |
| :--- | :--- | :--- |
| **Valid JSON**, confidence &ge; 0.7, action matches deterministic policy | Accept diagnosis as explanation; deterministic policy authorizes action. | `RECOVERED` (if retry passes) |
| **Action not on allowlist** or conflicts with deterministic category | **Ignore AI action**; log policy conflict; execute deterministic rule. | Follows deterministic rule |
| **Invalid JSON**, missing fields, or unknown enum (`AT-05`) | **Reject AI output**; log `SAFE_FALLBACK`; execute deterministic recovery. | `SAFE_FALLBACK` / `NEEDS_REVIEW` |
| **Low confidence** (< 0.7) | Flag for human inspection. | `NEEDS_REVIEW` |
| **Model timeout, network down, or missing key (`AT-06`)** | Use static fallback diagnosis; deterministic recovery path unchanged. | `SAFE_FALLBACK` |

---

## 6. Static Fallback Diagnosis
When the model is unreachable, timeout occurs, or the API key is unavailable, FlowGuard uses this static fallback:

```json
{
  "failure_type": "UNKNOWN",
  "confidence": 0.0,
  "suggested_action": "STOP_AND_REVIEW",
  "rationale": "Static fallback: AI model unavailable or unresponsive. Deterministic policy rules remain authoritative.",
  "fallback_used": true
}
```
