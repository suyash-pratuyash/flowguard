from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def post(request_id, scenario, attempt, payload):
    return client.post(
        "/api/target",
        json={
            "request_id": request_id,
            "scenario": scenario,
            "attempt": attempt,
            "payload": payload,
        },
    )


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "flowguard-demo-api"}


def test_success_at01():
    r = post("t-success", "SUCCESS", 1, {"requiredField": "demo"})
    assert r.status_code == 200
    assert r.json() == {"request_id": "t-success", "attempt": 1, "status": "ok"}


def test_rate_limit_then_success_at02():
    first = post("t-429", "RATE_LIMIT_ONCE", 1, {"requiredField": "demo"})
    assert first.status_code == 429
    assert first.headers["retry-after"] == "2"
    assert first.json()["error"] == "RATE_LIMITED"
    assert first.json()["retryable"] is True

    second = post("t-429", "RATE_LIMIT_ONCE", 2, {"requiredField": "demo"})
    assert second.status_code == 200
    body = second.json()
    assert body["status"] == "ok"
    assert body["request_id"] == "t-429"
    assert body["attempt"] == 2


def test_service_unavailable_stays_503_at03():
    for attempt in (1, 2):
        r = post("t-503", "SERVICE_UNAVAILABLE", attempt, {})
        assert r.status_code == 503
        assert r.json()["error"] == "SIMULATED_UNAVAILABLE"


def test_missing_required_data_is_422_at04():
    r = post("t-invalid", "INVALID_DATA", 1, {})
    assert r.status_code == 422
    body = r.json()
    assert body["recoverable"] is False
    assert body["field"] == "requiredField"


def test_blank_required_data_is_422():
    assert post("t-blank", "INVALID_DATA", 1, {"requiredField": "   "}).status_code == 422
    assert post("t-num", "INVALID_DATA", 1, {"requiredField": 5}).status_code == 422


def test_valid_data_in_invalid_scenario_is_200():
    r = post("t-ok", "INVALID_DATA", 1, {"requiredField": "x"})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_unknown_scenario_rejected():
    assert post("t-x", "NOPE", 1, {}).status_code == 422


def test_attempt_out_of_range_rejected():
    assert post("t-a", "SUCCESS", 0, {}).status_code == 422
    assert post("t-a", "SUCCESS", 6, {}).status_code == 422
