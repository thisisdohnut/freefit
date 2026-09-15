from __future__ import annotations

import math
from datetime import datetime, timezone
from .core import Endpoint, summarize, now_iso


def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def inv_latency(ms: float | None, target: float = 1000.0) -> float:
    if ms is None or ms <= 0:
        return 0.0
    return clamp(100.0 * target / (target + ms))


def speed_score(stats: dict) -> float:
    ttft = inv_latency(stats.get("ttft_p50_ms"), 500)
    tps = stats.get("tps_p50")
    tps_score = clamp((tps or 0) / 400.0 * 100)
    return 0.45 * ttft + 0.55 * tps_score


def reliability_score(stats: dict) -> float:
    success = stats.get("success_rate", 0.0) * 100
    timeout = stats.get("timeout_rate", 1.0)
    r429 = stats.get("429_rate", 1.0)
    return clamp(0.50 * success + 0.20 * (100 * (1-timeout)) + 0.15 * (100 * (1-r429)) + 0.15 * success)


def free_value(ep: Endpoint) -> float:
    return {"F0": 100, "F1": 90, "F2": 75, "F3": 50, "F4": 40}.get(ep.free_class, 0)


def freshness(measured_at: str | None, ttl_seconds: float = 900) -> float:
    if not measured_at:
        return 0.0
    try:
        t = datetime.fromisoformat(measured_at.replace("Z", "+00:00"))
        age = max(0.0, (datetime.now(timezone.utc) - t).total_seconds())
        return math.exp(-age / ttl_seconds) * 100
    except Exception:
        return 0.0


def score_endpoint(ep: Endpoint, results: list) -> dict:
    stats = summarize(results)
    speed = speed_score(stats)
    reliability = reliability_score(stats)
    free = free_value(ep)
    measured = results[0].completed_at if results else None
    fresh = freshness(measured)
    samples = stats.get("samples", 0)
    stability = 1.0 if samples >= 10 else samples / 10.0
    success = stats.get("success_rate", 0.0)
    confidence = clamp(100 * stability * max(0.0, min(1.0, success))) / 100.0
    raw = 0.25 * speed + 0.20 * reliability + 0.15 * free + 0.10 * fresh + 30.0
    final = clamp(raw * confidence)
    return {
        "measured_at": measured or now_iso(),
        "score": final,
        "speed": speed,
        "reliability": reliability,
        "free_value": free,
        "freshness": fresh,
        "confidence": confidence,
        "stats": stats,
        "explanation": {
            "speed": speed,
            "reliability": reliability,
            "free_value": free,
            "freshness": fresh,
            "samples": samples,
            "confidence": confidence,
        },
    }


def rank(endpoints_with_scores: list[tuple[Endpoint, dict]]) -> list[tuple[Endpoint, dict]]:
    return sorted(endpoints_with_scores, key=lambda x: x[1]["score"], reverse=True)
