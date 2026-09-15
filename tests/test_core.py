from freefit.core import classify_http, estimate_tokens, summarize, ProbeResult


def test_http_classes():
    assert classify_http(429) == "RATE_LIMITED"
    assert classify_http(500) == "SERVER_ERROR"
    assert classify_http(404) == "NOT_FOUND"


def test_token_estimate_positive():
    assert estimate_tokens("hello world") >= 1


def test_summary():
    r = ProbeResult("x", "2026-01-01T00:00:00+00:00", "2026-01-01T00:00:01+00:00", 100, 900, 1000, 90, 100, 200, True)
    s = summarize([r])
    assert s["samples"] == 1
    assert s["success_rate"] == 1.0
    assert s["ttft_p50_ms"] == 100
