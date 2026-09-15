# Fallback Specification

## Objective

Ensure a request can complete when the preferred endpoint is slow, rate-limited, unavailable or policy-invalid.

## Fallback order

```text
Primary
  ↓ timeout / hard failure
Same-model alternate provider
  ↓ failure
Same-capability alternate model
  ↓ failure
General-purpose safe endpoint
  ↓ failure
Local endpoint (optional)
```

## Retry policy

Retry only errors likely to succeed on retry:

```text
429             → backoff + alternate endpoint
408/timeout     → alternate endpoint
5xx             → bounded retry / alternate
network         → bounded retry / alternate
4xx auth        → do not blindly retry
invalid request → do not retry
```

Use exponential backoff with jitter. Never create an unbounded retry loop.

## Circuit breaker

```text
CLOSED
  ↓ repeated failures
OPEN
  ↓ probe interval
HALF_OPEN
  ├── success → CLOSED
  └── failure → OPEN
```

## Fallback score

Fallback candidates are scored under the same routing constraints, but availability/reliability gets a higher temporary weight.

## Context transfer

When falling back, preserve the required conversation context if token limits allow. If not, use a documented compaction strategy rather than silently truncating critical instructions.

## Observability

Every fallback emits an event:

```yaml
event: ROUTE_FALLBACK
primary: groq/gpt-oss-120b
fallback: nvidia/nemotron-3-ultra
reason: timeout
attempt: 2
timestamp: ...
```
