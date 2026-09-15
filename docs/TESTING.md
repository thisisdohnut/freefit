# Testing Strategy

## Test layers

### Unit

Test normalization, percentile calculations, scoring, policy classification, routing filters and circuit transitions without network access.

### Contract

Each provider adapter must pass the same normalized request/response contract tests.

### Integration

Run against provider sandboxes or selected live endpoints under explicit opt-in.

### Benchmark validation

Verify timing instrumentation against a local fake streaming server with known delays.

### Failure injection

Simulate:

```text
429
408
500
503
timeout
connection reset
malformed stream
missing usage metadata
expired quota
catalog outage
```

## Golden fixtures

Keep provider responses as redacted fixtures so parser behavior is reproducible without live credentials.

## Routing tests

Given the same registry + telemetry snapshot, routing must be deterministic unless a policy explicitly uses randomized exploration.

## Performance tests

The TUI must remain responsive while benchmark/discovery jobs run asynchronously. Network work must never block keyboard navigation or rendering.

## Acceptance criteria

- one bad provider cannot crash the process
- JSON output schema remains backward compatible within a minor release
- stale data is visibly marked
- routing excludes hard-ineligible endpoints
- fallback terminates within configured retry limits
