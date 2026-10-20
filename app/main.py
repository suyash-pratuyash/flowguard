"""FlowGuard fault-injection API (spec/03-api-contract.md v1.0).

Safe mock service: no external calls, no side effects, no secrets.
It only returns deterministic responses. Recovery policy lives in the orchestrator (n8n).
"""
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="FlowGuard Demo API", version="0.1.0")

Scenario = Literal[
    "SUCCESS",
    "RATE_LIMIT_ONCE",
    "SERVICE_UNAVAILABLE",
    "INVALID_DATA",
]


class TargetRequest(BaseModel):
    request_id: str = Field(min_length=1, max_length=80)
    scenario: Scenario
    attempt: int = Field(ge=1, le=5)
    payload: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health():
    return {"status": "ok", "service": "flowguard-demo-api"}


@app.post("/api/target")
def target(req: TargetRequest):
    base = {"request_id": req.request_id, "attempt": req.attempt}

    if req.scenario == "SUCCESS":
        return {**base, "status": "ok"}

    if req.scenario == "RATE_LIMIT_ONCE":
        if req.attempt == 1:
            return JSONResponse(
                status_code=429,
                content={"error": "RATE_LIMITED", "retryable": True, **base},
                headers={"Retry-After": "2"},
            )
        return {**base, "status": "ok"}

    if req.scenario == "SERVICE_UNAVAILABLE":
        return JSONResponse(
            status_code=503,
            content={"error": "SIMULATED_UNAVAILABLE", "retryable": True, **base},
        )

    if req.scenario == "INVALID_DATA":
        value = req.payload.get("requiredField")
        if not isinstance(value, str) or not value.strip():
            return JSONResponse(
                status_code=422,
                content={
                    "error": "INVALID_DATA",
                    "field": "requiredField",
                    "recoverable": False,
                    **base,
                },
            )
        return {**base, "status": "ok"}

    # Literal validation makes this unreachable.
    return JSONResponse(status_code=400, content={"error": "UNSUPPORTED_SCENARIO"})
