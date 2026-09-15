# Health Monitoring

## Health dimensions

Health is multi-dimensional:

```text
availability
latency
error rate
rate-limit pressure
quota state
stream integrity
catalog freshness
```

## Probe classes

### Liveness

Can the endpoint return a valid minimal completion?

### Readiness

Can it satisfy the normal routing contract: streaming, structured output, tools, or other declared capabilities?

### Performance

Is it within acceptable TTFT/TPS/latency bounds?

## State calculation

```text
UNKNOWN
  ↓
PROBING
  ↓
HEALTHY
  ├── latency regression → DEGRADED
  ├── repeated 429        → RATE_LIMITED
  ├── repeated timeout    → DOWN
  └── auth failure        → CONFIG_ERROR
```

## Example thresholds

```yaml
healthy:
  success_rate: >= 99%
  timeout_rate: < 1%
  p95_ttft_multiplier: < 1.5

degraded:
  success_rate: 95-99%
  or p95_ttft_multiplier: 1.5-3.0

down:
  success_rate: < 95%
  or consecutive_failures: >= 3
```

Thresholds are policy defaults and must be configurable per provider/workload.

## Hysteresis

Do not flip between healthy and degraded on every sample. Require repeated evidence for transitions and fewer failures to recover.

## Circuit breaker

```text
CLOSED → OPEN → HALF_OPEN → CLOSED
```

When open, the router should stop normal traffic to the endpoint while scheduled probes test recovery.
