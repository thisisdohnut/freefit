# Router Specification

## Purpose

Select the best eligible endpoint for each request using hard constraints plus live scoring.

## Request profile

```yaml
workload: coding
latency_budget_ms: 2000
min_quality: 0.80
free_required: true
streaming_required: true
tools_required: false
context_tokens: 16000
region_preference: null
max_retries: 2
```

## Routing pipeline

```text
request
  ↓
classify workload
  ↓
load candidate endpoints
  ↓
apply hard constraints
  ↓
filter unhealthy / exhausted
  ↓
score candidates
  ↓
diversity / anti-repeat policy
  ↓
choose primary
  ↓
execute
  ↓
evaluate
  ↓
update telemetry
```

## Hard constraints

Reject endpoints that:

- cannot satisfy required modality/capability
- are outside explicit free policy when free-only is required
- are circuit-open
- have exhausted quota
- cannot meet context requirement
- lack required streaming/tool contract

## Soft objectives

Optimize:

1. reliability
2. latency
3. quality
4. free value
5. throughput

Ordering can change by workload.

## Anti-flapping

Do not switch providers because of tiny score differences. Use a minimum margin:

```text
new_score >= current_score + switch_margin
```

Also require a cooldown after a successful route unless the current endpoint becomes unhealthy.

## Request stickiness

For multi-turn sessions, preserve endpoint/provider affinity where practical to reduce behavior changes, subject to health and quota constraints.

## Route explanation

The router must expose:

```text
selected: Groq / GPT-OSS 120B
score: 97.1
reason: fastest healthy coding endpoint with F0 free policy
fallback: NVIDIA / Nemotron 3 Ultra
```

## Routing matrix

```text
                 CHAT  CODE  REASON  JSON  TOOLS  VISION
Groq              95    98     91     97     94      --
Google            96    88     94     93     90      98
NVIDIA             92    94     96     95     97      91
OpenRouter         89    91     90     92     88      90
```

Values are examples of the UI contract, not benchmark results.
