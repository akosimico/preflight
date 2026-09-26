from core.dashboard_analytics import recent_series
from runners.api_runner import MAX_RESPONSE_CHARS, prepare_response


def test_prepare_response_redacts_json_and_truncates_large_content():
    assert "[REDACTED]" in prepare_response('{"token":"secret","name":"safe"}')
    value = prepare_response("x" * (MAX_RESPONSE_CHARS + 1))
    assert "Response truncated" in value and len(value) > MAX_RESPONSE_CHARS


def test_recent_series_uses_relevant_runs_and_derives_percentages():
    runs = [
        {"id": 1, "created_at": "2026-01-01 00:00:00", "summary_json": {"passed": 9, "total": 10}},
        {"id": 2, "created_at": "2026-01-02 00:00:00", "summary_json": {}},
        {"id": 3, "created_at": "2026-01-03 00:00:00", "summary_json": {"security_check": True, "findings": 2}},
    ]
    metrics = {2: [{"average_ms": 100, "p95_ms": 150, "error_rate": 5}]}
    series = recent_series(runs, lambda run_id: metrics.get(run_id, []))
    assert series["api"][0]["value"] == 90
    assert series["load"][0]["success_rate"] == 95
    assert series["security"][0]["findings"] == 2
