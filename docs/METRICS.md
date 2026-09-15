# Metrics Specification

## Principles

Metrics must be comparable, reproducible and time-aware. A number without unit, sample count and timestamp is not a routing-grade metric.

## Latency

### TTFT — Time to First Token

Elapsed time from request dispatch to the first streamed output token/chunk accepted from the provider.

```text
TTFT = first_token_timestamp - request_start_timestamp
```

Track:

- median / P50
- P90
- P95
- P99
- minimum / maximum

### Queue latency

Where detectable, distinguish provider queue time from model execution time. Do not fabricate this value when the provider does not expose it.

### Total latency

```text
Total = response_end - request_start
```

Report together with input and output token counts.

## Throughput

### Output tokens per second

```text
TPS = generated_output_tokens / generation_time_seconds
```

Generation time should exclude TTFT when comparing decoding speed.

### End-to-end token throughput

```text
E2E_TPS = (input_tokens + output_tokens) / total_elapsed_seconds
```

Use carefully because it mixes prompt processing and generation.

## Reliability

```text
success_rate = successful_requests / total_requests
error_rate   = failed_requests / total_requests
429_rate     = 429 responses / total_requests
5xx_rate     = 5xx responses / total_requests
timeout_rate = timed_out_requests / total_requests
```

Track retry outcomes separately from first-attempt outcomes.

## Freshness

```text
age = now - observation.timestamp
```

A stale excellent score must not outrank a fresh mediocre measurement without a policy reason.

## Free-state metrics

Track:

- `free_class`
- `quota_remaining`
- `quota_unit`
- `quota_reset_at`
- `rate_limit_remaining`
- `rate_limit_reset_at`
- `free_policy_verified_at`
- `free_policy_source`

## Quality metrics

Quality is workload-specific. Do not collapse all quality into a single permanent model number.

Minimum categories:

```text
chat
coding
reasoning
json
tool_call
long_context
vision
structured_output
```

## Measurement provenance

Every dynamic metric includes:

```yaml
source: direct_probe
provider: groq
model: openai/gpt-oss-120b
region: us-east
network: residential
measured_at: 2026-09-15T12:00:00Z
sample_count: 20
benchmark_version: 0.1
```

## Confidence

Confidence increases with sample count, recency and consistency.

A simple v0.1 formulation:

```text
confidence = sample_factor × freshness_factor × stability_factor
```

Cap confidence when samples are too few or errors are too high.

## Recommended retention

Raw probe samples: 7–30 days depending on storage.

Aggregates:

- 1-minute: 24h
- 5-minute: 7d
- hourly: 30d
- daily: 1y

These defaults are configurable.
