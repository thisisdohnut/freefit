# FREEFIT

**Free Inference Fitness & Intelligence Tracker**

FREEFIT is a provider-aware control plane for discovering, measuring, ranking, routing, and monitoring free/free-tier LLM inference endpoints.

> Goal: make it obvious which model + provider is fastest, healthiest, cheapest/free, and most reliable **right now**.

## What is implemented

FREEFIT now contains a runnable Python core with:

- SQLite endpoint + probe + score telemetry store
- OpenAI-compatible provider adapter
- streaming TTFT measurement
- output token/sec measurement
- P50/P95 summaries
- reliability / 429 / timeout tracking
- live score calculation with confidence
- dense Rich terminal board
- live observatory with sparklines
- JSON output for agents/scripts
- repeatable benchmark command
- configuration-driven provider/model registry
- doctor diagnostics

The provider layer is intentionally adapter-based. Any provider exposing OpenAI-compatible `/models` and `/chat/completions` can be added without changing the scoring or TUI layers.

## Install

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e .
Copy-Item freefit.example.json freefit.json
```

Set the provider API keys used by your config. Example:

```powershell
$env:GROQ_API_KEY = "..."
$env:NVIDIA_API_KEY = "..."
$env:OPENROUTER_API_KEY = "..."
$env:OPENCODE_API_KEY = "..."
```

Never commit `freefit.json`, API keys, or the local `.freefit/` database.

## Run

Open the live observatory:

```bash
freefit
```

Show endpoint rankings:

```bash
freefit models
freefit models --free-only
```

Run a single live probe:

```bash
freefit probe groq:openai/gpt-oss-120b
```

Benchmark configured endpoints:

```bash
freefit bench --runs 5 --warmup 1
```

Agent-friendly JSON:

```bash
freefit --json status
freefit models --json
freefit bench --json
```

Diagnostics:

```bash
freefit doctor
```

## TUI / graphics

FREEFIT follows the information density that makes llmfit useful, while changing the unit of analysis from **local model × hardware** to **cloud endpoint × provider × live conditions**.

The primary board exposes:

```text
STATE  MODEL  PROVIDER  FREE  SCORE  TTFT  TOK/S  P95  429  CONF
```

The observatory adds rolling sparklines:

```text
TTFT  ▂▂▃▄▅▇█▆▄▃
TPS   █▇▇▆▄▂▂▃▅▆
```

See [`docs/LLMFIT-REVIEW.md`](docs/LLMFIT-REVIEW.md) and [`docs/TUI-DESIGN.md`](docs/TUI-DESIGN.md) for the full visual system.

## Architecture

```text
Discovery
   ↓
Registry
   ↓
Health
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

The current release implements the local registry, probe, benchmark, scoring, store, CLI and TUI layers. Router/fallback/discovery schedulers are defined by the contracts and are the next implementation layer.

## Important measurement rule

FREEFIT measures **the endpoint**, not just the model name. The same model can have different TTFT, throughput, quota and reliability across providers. Scores always retain timestamp, sample count and provenance.

## Documentation

See `docs/` for the architecture, benchmark methodology, metrics, provider contract, routing policy, security model and roadmap.

## Status

**v0.1.0 — runnable local control-plane core**

Live measurements require valid provider credentials and a configured `freefit.json`. Provider catalogs, free policies and model IDs can change over time; the registry is deliberately configurable rather than embedding a permanent global “free model” truth.
