# Scoring Specification

## Objective

Produce a routing score that represents current endpoint fitness, not a permanent model ranking.

## Dimensions

Default v0.1 weights:

```text
Quality       25%
Speed         25%
Reliability   20%
Free-value    15%
Freshness     10%
Capability     5%
```

Weights are configurable by workload profile.

## Speed score

Normalize TTFT and TPS separately against a candidate pool, then combine them:

```text
speed = 0.45 × ttft_score + 0.55 × tps_score
```

Lower TTFT is better. Higher TPS is better.

Use robust percentile values rather than single samples.

## Reliability score

```text
reliability =
  0.50 × success_score
+ 0.20 × (1 - timeout_rate)
+ 0.15 × (1 - 429_rate)
+ 0.15 × stability_score
```

## Freshness score

A simple decay model:

```text
freshness = exp(-age / ttl)
```

Never allow stale data to appear equivalent to fresh data.

## Free-value score

Example:

```text
F0 permanent $0           = 100
F1 active free quota      = 90
F2 limited-time free      = 75
F3 trial credit           = 50
F4 local-only             = 40
UNKNOWN                   = 0
```

Actual values are product policy, not provider claims.

## Quality

Quality must depend on workload. Maintain benchmark dimensions instead of one immutable quality number.

## Confidence adjustment

```text
final_score = raw_score × confidence
```

A low-sample result must not outrank a well-measured result solely because of a noisy fast sample.

## Penalties

Apply explicit penalties for:

- active circuit breaker
- quota exhaustion
- expired free status
- high 429 rate
- stale measurements
- unsupported required capability
- provider policy uncertainty

## Score explainability

Every routing score should produce an explanation:

```text
Score 91.2

+ 24.1 quality
+ 22.8 speed
+ 19.7 reliability
+ 14.0 free-value
+  8.7 freshness
+  2.4 capability

Penalty -0.5 quota pressure
```

## Ranking rule

Never sort only on score when hard constraints are present. Apply hard constraints first, then rank eligible endpoints.
