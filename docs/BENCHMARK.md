# Benchmark Specification

## Goal

Measure endpoint performance using controlled, repeatable requests so FREEFIT can rank live endpoints rather than rely on marketing claims or stale catalogs.

## Benchmark layers

### Layer 0 — health probe

Minimal request to prove authentication, connectivity and response validity.

### Layer 1 — speed probe

Streaming request with a fixed prompt and bounded output. Measures TTFT, TPS and total latency.

### Layer 2 — workload benchmark

Role-specific prompts for coding, reasoning, JSON, tools, long context and multimodal tasks.

### Layer 3 — reliability soak

Repeated probes over an interval to expose intermittent 429s, timeouts and degradation.

## Standard speed probe

The default speed probe should:

- use `stream=true` when supported
- request a deterministic output size range
- use a stable system prompt
- avoid huge context unless testing long-context behavior
- record timestamps at dispatch, first byte/token, every chunk, and final completion

## Sampling

Recommended default:

```yaml
warmup_runs: 2
measured_runs: 10
max_concurrency: 1
request_timeout: 60s
```

For production routing calibration, use more samples and multiple time windows.

## Workload suite

```text
W01 chat-short       small factual response
W02 chat-stream      natural streaming response
W03 coding           code generation/fix
W04 reasoning        multi-step problem
W05 json             strict JSON schema
W06 tool             tool-call/function-call contract
W07 long-context     large prompt + short answer
W08 vision           image + text, where supported
W09 multilingual     English/Malay mixed prompt
W10 agent            plan + action-oriented response
```

## Fairness controls

Benchmark records must include:

- provider endpoint
- model ID
- region
- API mode
- prompt tokens
- requested max output tokens
- temperature/seed when supported
- concurrency
- client/runtime version
- timestamp

Do not compare measurements taken under incompatible request parameters without labeling the difference.

## Outlier handling

Do not silently delete failures. Store them.

For throughput statistics, use robust aggregates such as median and P95. Keep raw samples for auditability.

## Benchmark result

Example:

```json
{
  "endpoint": "groq/openai/gpt-oss-120b",
  "workload": "W03",
  "samples": 10,
  "ttft_p50_ms": 192,
  "ttft_p95_ms": 420,
  "tps_p50": 408,
  "tps_p95": 351,
  "total_p50_ms": 540,
  "success_rate": 1.0,
  "429_rate": 0.0,
  "timeout_rate": 0.0
}
```

## Benchmark versioning

Every run records `benchmark_version`. Changing prompts, timing semantics or token counting rules must increment the benchmark version.
