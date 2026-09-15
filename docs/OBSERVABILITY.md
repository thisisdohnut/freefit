# Observability

## Goals

Answer three questions quickly:

1. What is fast now?
2. What became unhealthy?
3. Why did the router choose this endpoint?

## Metrics streams

```text
probe latency
probe throughput
HTTP status
429 rate
timeouts
quota pressure
score changes
route decisions
fallbacks
```

## Event types

```text
DISCOVERY_CHANGED
HEALTH_CHANGED
PROBE_COMPLETED
BENCHMARK_COMPLETED
SCORE_CHANGED
QUOTA_CHANGED
ROUTE_SELECTED
ROUTE_FALLBACK
CIRCUIT_OPENED
CIRCUIT_CLOSED
```

## Incident timeline

The TUI observatory should render events chronologically with severity and affected endpoint.

```text
14:10 🟢 Groq probe healthy       0.19s / 412 tok/s
14:15 🟡 Groq TTFT P95 increased  +74%
14:17 🔴 Groq 429 spike           8.1%
14:18 🔀 router switched          → NVIDIA
14:26 🟢 Groq recovered            0.31s / 381 tok/s
```

## Logging

Structured logs must include correlation IDs for route attempts and benchmark runs. Never log API keys or raw sensitive prompts by default.

## Debug mode

Debug output may include provider request timing and normalized error class, but secrets must remain redacted.
