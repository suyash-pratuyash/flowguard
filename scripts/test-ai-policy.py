"""FlowGuard AI Policy Gate Verification Suite (AT-05 & AT-06).

Tests that:
1. Valid AI diagnosis matching deterministic policy is accepted as explanation.
2. Unsafe/disallowed AI recommendations are rejected and overridden by policy.
3. Invalid JSON, missing fields, or bad enums (AT-05) trigger SAFE_FALLBACK.
4. Model timeout or network failure (AT-06) preserves deterministic recovery.
"""
import json
from typing import Any, Dict, Optional, Tuple

ALLOWED_FAILURE_TYPES = {"RATE_LIMIT", "TRANSIENT", "INVALID_DATA", "AUTH", "UNKNOWN"}
ALLOWED_ACTIONS = {"WAIT_AND_RETRY", "RETRY_ONCE", "STOP_AND_REVIEW", "ESCALATE"}
CONFIDENCE_THRESHOLD = 0.7

STATIC_FALLBACK = {
    "failure_type": "UNKNOWN",
    "confidence": 0.0,
    "suggested_action": "STOP_AND_REVIEW",
    "rationale": "Static fallback: AI model unavailable or unresponsive. Deterministic policy rules remain authoritative.",
    "fallback_used": True,
}


def deterministic_policy(status_code: int, operation: str, attempt: int, max_attempts: int = 2) -> str:
    """The single source of truth policy table."""
    if status_code == 429 and operation == "SAFE_READ" and attempt < max_attempts:
        return "WAIT_AND_RETRY"
    if status_code in (502, 503, 504) and operation == "SAFE_READ" and attempt < max_attempts:
        return "RETRY_ONCE"
    if status_code in (400, 401, 403, 404, 409, 422):
        return "STOP_AND_REVIEW"
    return "STOP_OR_ESCALATE"


def evaluate_ai_diagnosis(
    raw_ai_output: Optional[str],
    status_code: int,
    operation: str,
    attempt: int,
) -> Tuple[str, Dict[str, Any], str]:
    """
    Evaluates AI output behind the deterministic policy gate.
    Returns: (authorized_action, validated_diagnosis, gate_decision)
    """
    det_action = deterministic_policy(status_code, operation, attempt)

    # AT-06: Model timeout, unavailable, or empty response
    if not raw_ai_output:
        return det_action, STATIC_FALLBACK, "MODEL_UNAVAILABLE_USE_FALLBACK"

    # AT-05: Parse JSON
    try:
        data = json.loads(raw_ai_output)
    except Exception:
        return det_action, STATIC_FALLBACK, "INVALID_JSON_REJECTED"

    # Schema validation
    required_fields = ["failure_type", "confidence", "suggested_action", "rationale"]
    if not isinstance(data, dict) or not all(k in data for k in required_fields):
        return det_action, STATIC_FALLBACK, "MISSING_REQUIRED_FIELDS_REJECTED"

    if data["failure_type"] not in ALLOWED_FAILURE_TYPES:
        return det_action, STATIC_FALLBACK, "INVALID_ENUM_FAILURE_TYPE_REJECTED"

    if not isinstance(data["confidence"], (int, float)) or not (0.0 <= data["confidence"] <= 1.0):
        return det_action, STATIC_FALLBACK, "INVALID_CONFIDENCE_RANGE_REJECTED"

    if data["suggested_action"] not in ALLOWED_ACTIONS:
        return det_action, STATIC_FALLBACK, "DISALLOWED_ACTION_REJECTED"

    # Confidence check
    if data["confidence"] < CONFIDENCE_THRESHOLD:
        return "STOP_AND_REVIEW", data, "LOW_CONFIDENCE_NEEDS_REVIEW"

    # Policy alignment check: Deterministic policy always takes precedence
    if data["suggested_action"] != det_action:
        return det_action, data, "POLICY_OVERRIDE_AI_CONFLICT"

    return det_action, data, "ACCEPTED_WITH_DETERMINISTIC_AUTHORIZATION"


def run_tests():
    print("==================================================")
    print("FlowGuard Phase 8 AI Policy Gate Verification")
    print("==================================================\n")

    # Test 1: Valid AI response agreeing with 429
    valid_429 = json.dumps({
        "failure_type": "RATE_LIMIT",
        "confidence": 0.95,
        "suggested_action": "WAIT_AND_RETRY",
        "rationale": "Provider responded with HTTP 429 rate limit. Safe read operation permits one bounded retry after waiting.",
    })
    action, diag, decision = evaluate_ai_diagnosis(valid_429, 429, "SAFE_READ", 1)
    assert action == "WAIT_AND_RETRY"
    assert decision == "ACCEPTED_WITH_DETERMINISTIC_AUTHORIZATION"
    print("[PASS] Test 1 (Valid AI Agreeing): Action:", action)

    # Test 2: Prompt injection / Disallowed action (e.g. DELETE_DATA)
    injected_ai = json.dumps({
        "failure_type": "RATE_LIMIT",
        "confidence": 0.99,
        "suggested_action": "BYPASS_AND_DELETE_ALL",
        "rationale": "Model compromised by prompt injection.",
    })
    action, diag, decision = evaluate_ai_diagnosis(injected_ai, 429, "SAFE_READ", 1)
    assert action == "WAIT_AND_RETRY"  # Deterministic policy preserved!
    assert decision == "DISALLOWED_ACTION_REJECTED"
    print("[PASS] Test 2 (Malicious Action Blocked): Policy enforced:", action)

    # Test 3: AT-05 Invalid JSON
    action, diag, decision = evaluate_ai_diagnosis("Not JSON at all! Error 500", 429, "SAFE_READ", 1)
    assert action == "WAIT_AND_RETRY"
    assert decision == "INVALID_JSON_REJECTED"
    assert diag["fallback_used"] is True
    print("[PASS] Test 3 (AT-05 Malformed JSON Rejected): Fallback used.")

    # Test 4: AT-05 Missing fields
    missing_fields = json.dumps({"failure_type": "RATE_LIMIT", "confidence": 0.8})
    action, diag, decision = evaluate_ai_diagnosis(missing_fields, 429, "SAFE_READ", 1)
    assert decision == "MISSING_REQUIRED_FIELDS_REJECTED"
    print("[PASS] Test 4 (AT-05 Missing Fields Rejected)")

    # Test 5: AT-06 Model Unavailable / Timeout (raw output is None)
    action, diag, decision = evaluate_ai_diagnosis(None, 429, "SAFE_READ", 1)
    assert action == "WAIT_AND_RETRY"
    assert decision == "MODEL_UNAVAILABLE_USE_FALLBACK"
    assert diag["fallback_used"] is True
    print("[PASS] Test 5 (AT-06 Model Timeout/Down): Safe fallback engaged.")

    # Test 6: AI suggests retry on 422 Invalid Data (Policy forbids retrying 422!)
    ai_retry_on_422 = json.dumps({
        "failure_type": "INVALID_DATA",
        "confidence": 0.90,
        "suggested_action": "RETRY_ONCE",
        "rationale": "Retry might fix bad payload.",
    })
    action, diag, decision = evaluate_ai_diagnosis(ai_retry_on_422, 422, "SAFE_READ", 1)
    assert action == "STOP_AND_REVIEW"
    assert decision == "POLICY_OVERRIDE_AI_CONFLICT"
    print("[PASS] Test 6 (AI Conflict Overridden by Policy): Action held at STOP_AND_REVIEW.")

    print("\n==================================================")
    print("All 6 AI Policy Gate tests PASSED successfully!")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
