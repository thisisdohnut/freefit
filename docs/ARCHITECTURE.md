# FREEFIT Architecture

## 1. Mission

FREEFIT is a control plane that continuously answers:

> Which free/free-tier LLM endpoint should receive this request **right now**?

It combines static catalog facts with dynamic measurements.

## 2. Logical architecture

```text
┌──────────────────────┐
│   MODEL DISCOVERY    │  provider catalogs / APIs / config
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│      REGISTRY        │  provider/model/endpoint identities
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│   HEALTH MONITOR     │  availability + policy checks
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│    SPEED PROBE       │  TTFT / TPS / total latency
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│      BENCHMARK       │  standard workloads + capability tests
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│      SCORING         │  quality + speed + reliability + free state
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│       ROUTER         │  choose endpoint for request profile
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│     EVALUATOR        │  assess outcome and policy compliance
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│      LEARNING        │  update weights from observed outcomes
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│      FALLBACK        │  retry / failover / circuit breaker
└──────────────────────┘
```

## 3. Core separation

### Control plane

Maintains knowledge and decisions:

- catalog discovery
- health state
- measurements
- scoring
- policies
- quotas
- routing
- history

### Data plane

Executes user requests against selected providers.

The data plane must not need to understand every provider's quirks. Provider adapters normalize requests and responses.

## 4. Endpoint identity

The routing object is:

```text
Endpoint = provider + model + deployment/region + API mode
```

Never use only `model_name` as the identity because the same model can have materially different latency, quota, reliability and pricing across providers.

## 5. Runtime components

```text
freefit-cli
    │
    ├── registry service
    ├── probe scheduler
    ├── benchmark runner
    ├── scoring engine
    ├── routing engine
    ├── provider adapters
    ├── local store
    └── API server
```

The first implementation may keep these in one process. The architecture must allow them to split later.

## 6. Event-driven state

Important state transitions are events:

```text
DISCOVERED
→ VERIFIED
→ PROBING
→ HEALTHY
→ DEGRADED
→ RATE_LIMITED
→ QUOTA_EXHAUSTED
→ DOWN
→ RECOVERING
→ HEALTHY
```

Events must be timestamped and retained so the reason for a routing change can be reconstructed.

## 7. Freshness

Dynamic data has a TTL. Example defaults:

```yaml
health_ttl: 120s
speed_ttl: 15m
benchmark_ttl: 24h
quota_ttl: 5m
catalog_ttl: 6h
```

These are defaults, not universal truth. Provider-specific policies may override them.

## 8. Failure isolation

A provider adapter must fail independently. An exception from one provider cannot terminate discovery, probing or routing for all other providers.

## 9. Data quality hierarchy

When values conflict, prefer:

```text
fresh direct measurement
  > recent trusted community measurement
  > provider-reported metric
  > static catalog fact
  > heuristic estimate
```

Each value should retain its provenance.
