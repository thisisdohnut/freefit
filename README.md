# FREEFIT

**Free Inference Fitness & Intelligence Tracker**

FREEFIT is a provider-aware control plane for discovering, measuring, ranking, routing, and monitoring free/free-tier LLM inference endpoints.

> Goal: make it obvious which model + provider is fastest, healthiest, cheapest/free, and most reliable **right now**.

## Why FREEFIT

Local LLM tools such as [llmfit](https://github.com/AlexsJones/llmfit) are excellent at matching models to local hardware and exposing a rich terminal UI. FREEFIT takes a different target: **cloud/API endpoint fitness over time**.

llmfit emphasizes hardware fit, model size, estimated/measured local throughput, fit, quality, context, and community benchmark views. FREEFIT emphasizes endpoint state: TTFT, output throughput, total latency, error/429 rate, quota, freshness, provider health, benchmark quality, and routing decisions.

## Core flow

```text
Discovery
   ↓
Registry
   ↓
Health Monitor
   ↓
Speed Probe
   ↓
Benchmark
   ↓
Scoring
   ↓
Router
   ↓
Evaluator
   ↓
Learning
   ↓
Fallback
```

## Primary product surfaces

- **FREEFIT TUI** — dense, interactive terminal dashboard.
- **Model detail view** — latency, throughput, reliability, capabilities, quota, history.
- **Provider view** — provider-wide health, rate limits, free-tier status and incidents.
- **Compare view** — compare models/endpoints side-by-side.
- **Live observatory** — live speed/health trends and degradation detection.
- **Routing matrix** — best endpoint per task profile.
- **JSON/API mode** — machine-readable output for Kimi Code, Hermes-Agent, scripts and other agents.

## Design principles

1. **Measured beats guessed.** Real probes outrank static estimates.
2. **Endpoint identity matters.** A model can be fast at one provider and slow at another.
3. **Freshness matters.** A score without a timestamp is unsafe for routing.
4. **Free is a policy state, not a boolean.** Permanent-free, quota-free, limited-time, trial-credit and local-only must be distinct.
5. **Never hide uncertainty.** Every score carries sample count, source and confidence.
6. **Fail gracefully.** One provider failure must not stop the router.

## Documentation map

| Document | Purpose |
|---|---|
| [`docs/SYSTEM-OVERVIEW.md`](docs/SYSTEM-OVERVIEW.md) | Product and subsystem overview |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Logical and runtime architecture |
| [`docs/LLMFIT-REVIEW.md`](docs/LLMFIT-REVIEW.md) | Review of llmfit UX and FREEFIT improvements |
| [`docs/TUI-DESIGN.md`](docs/TUI-DESIGN.md) | FREEFIT terminal UI and graphics system |
| [`docs/METRICS.md`](docs/METRICS.md) | Latency, throughput and reliability definitions |
| [`docs/BENCHMARK.md`](docs/BENCHMARK.md) | Benchmark methodology and workloads |
| [`docs/SCORING.md`](docs/SCORING.md) | Composite score and confidence model |
| [`docs/ROUTER.md`](docs/ROUTER.md) | Routing and decision policy |
| [`docs/FALLBACK.md`](docs/FALLBACK.md) | Failure handling and fallback chains |
| [`docs/REGISTRY.md`](docs/REGISTRY.md) | Provider/model/endpoint registry |
| [`docs/DATA-MODEL.md`](docs/DATA-MODEL.md) | Storage entities and relationships |
| [`docs/PROVIDERS.md`](docs/PROVIDERS.md) | Provider adapter contract |
| [`docs/DISCOVERY.md`](docs/DISCOVERY.md) | Live model/provider discovery |
| [`docs/HEALTH.md`](docs/HEALTH.md) | Health checks and degradation detection |
| [`docs/QUOTA.md`](docs/QUOTA.md) | Free-tier and rate-limit tracking |
| [`docs/CLI.md`](docs/CLI.md) | CLI commands and output contracts |
| [`docs/OBSERVABILITY.md`](docs/OBSERVABILITY.md) | Events, logs, traces and dashboards |
| [`docs/SECURITY.md`](docs/SECURITY.md) | API key and probe safety |
| [`docs/TESTING.md`](docs/TESTING.md) | Test strategy |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Delivery phases |

## Status

**Documentation foundation — v0.1**

This repository intentionally starts documentation-first so the implementation can follow stable contracts rather than repeated redesign.

## Reference research

- [llmfit](https://github.com/AlexsJones/llmfit)
- [llmfit TUI guide](https://github.com/AlexsJones/llmfit/blob/main/docs/tui.md)
- [llmfit benchmarking guide](https://github.com/AlexsJones/llmfit/blob/main/docs/benchmarking.md)
