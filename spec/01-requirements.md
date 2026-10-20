# 01 - Requirements
Owner: Member 3 | Status: DRAFT v1.0

| ID | Requirement | Pass condition | Status |
|---|---|---|---|
| FR-01 | Trigger a named deterministic scenario | Reviewer selects a supported scenario and runs it | planned |
| FR-02 | Capture failure context | Record scenario, request_id, attempt, status, safe error summary, timestamp | planned |
| FR-03 | Classify known failures deterministically | 429, 503, 422 map to agreed categories | planned |
| FR-04 | Bound actions by policy | Max 2 target attempts; only SAFE_READ auto-retries | planned |
| FR-05 | Stop malformed input | 422 ends in NEEDS_REVIEW before side effects | planned |
| FR-06 | Verify recovery | RECOVERED only after expected success response is checked | planned |
| FR-07 | Persist/display evidence | Execution history + audit record show decisions and final state | planned |
| FR-08 | Validate AI output (if implemented) | Schema/enums checked; invalid output rejected | planned (P2) |
| NFR-01 | Repeatability | 3 clean runs give expected outcomes | planned |
| NFR-02 | Bounded retry | Cap prevents infinite loop | planned |
| NFR-03 | Deterministic target | No external outage needed | planned |
| NFR-04 | Secret hygiene | No credentials in Git, prompts, logs, screenshots | planned |
| NFR-05 | Safe model failure | LLM timeout/invalid output cannot trigger forbidden action | planned (P2) |
| NFR-06 | Reproducibility | Teammate launches and tests from README alone | planned |
