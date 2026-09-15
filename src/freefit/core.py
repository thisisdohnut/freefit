from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from statistics import median, quantiles
from typing import Any
import math
import re


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def pct(values: list[float], p: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    qs = quantiles(values, n=100, method="inclusive")
    return qs[max(0, min(99, int(math.ceil(p)) - 1))]


@dataclass(slots=True)
class Endpoint:
    id: str
    provider: str
    model: str
    base_url: str
    api_style: str = "openai-compatible"
    free_class: str = "UNKNOWN"
    free_now: bool = False
    region: str = "global"
    streaming: bool = True
    tools: bool = False
    json_mode: bool = False
    vision: bool = False
    context_window: int | None = None
    enabled: bool = True


@dataclass(slots=True)
class ProbeResult:
    endpoint_id: str
    started_at: str
    completed_at: str
    ttft_ms: float | None
    generation_ms: float | None
    total_ms: float | None
    output_tokens: int
    tokens_per_second: float | None
    status_code: int | None
    success: bool
    error_class: str | None = None
    error_message: str | None = None
    estimated_tokens: bool = False
    request_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    # Portable approximation for providers that do not return usage on streams.
    return max(1, math.ceil(len(text) / 4))


def classify_http(code: int | None) -> str | None:
    if code is None:
        return "UNKNOWN"
    if code == 401 or code == 403:
        return "AUTH"
    if code == 404:
        return "NOT_FOUND"
    if code == 408:
        return "TIMEOUT"
    if code == 429:
        return "RATE_LIMITED"
    if 400 <= code < 500:
        return "INVALID_REQUEST"
    if 500 <= code < 600:
        return "SERVER_ERROR"
    return None


def normalize_model_name(model: str) -> str:
    model = re.sub(r"\s+", " ", model.strip())
    return model


def summarize(results: list[ProbeResult]) -> dict[str, Any]:
    ttft = [r.ttft_ms for r in results if r.ttft_ms is not None and r.success]
    tps = [r.tokens_per_second for r in results if r.tokens_per_second is not None and r.success]
    total = [r.total_ms for r in results if r.total_ms is not None and r.success]
    n = len(results)
    success = sum(1 for r in results if r.success)
    codes = [r.status_code for r in results]
    rate429 = sum(1 for c in codes if c == 429) / n if n else 0.0
    timeouts = sum(1 for r in results if r.error_class == "TIMEOUT") / n if n else 0.0
    out: dict[str, Any] = {
        "samples": n,
        "success_rate": success / n if n else 0.0,
        "429_rate": rate429,
        "timeout_rate": timeouts,
        "ttft_p50_ms": median(ttft) if ttft else None,
        "ttft_p95_ms": pct(ttft, 95) if ttft else None,
        "tps_p50": median(tps) if tps else None,
        "tps_p95": pct(tps, 95) if tps else None,
        "total_p50_ms": median(total) if total else None,
        "total_p95_ms": pct(total, 95) if total else None,
    }
    return out
