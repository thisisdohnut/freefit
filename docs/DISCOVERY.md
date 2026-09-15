# Live Model Discovery

## Objective

Continuously discover newly available models/endpoints and detect changes in provider catalogs and free policies.

## Sources

1. Provider-native model catalog APIs.
2. Provider documentation pages where no catalog API exists.
3. Manually pinned models in configuration.
4. Optional community/public catalogs.

## Discovery cycle

```text
fetch catalog
  ↓
normalize IDs
  ↓
diff against registry
  ↓
validate endpoint
  ↓
verify free policy
  ↓
upsert registry
  ↓
emit DISCOVERY_CHANGED
```

## Change types

```text
MODEL_ADDED
MODEL_REMOVED
MODEL_RENAMED
ENDPOINT_ADDED
ENDPOINT_REMOVED
FREE_STATUS_CHANGED
CAPABILITY_CHANGED
CONTEXT_CHANGED
POLICY_CHANGED
```

## Safety

Catalog ingestion is untrusted input. Never execute returned text as code or treat model names as shell arguments without escaping.

## Suggested schedule

- fast-moving provider catalog: 15–60 minutes
- slower provider catalog: 6–24 hours
- manual refresh: always available via CLI

## Reconciliation

A temporary provider API outage must not cause FREEFIT to delete an entire provider catalog. Mark the snapshot stale and retry.
