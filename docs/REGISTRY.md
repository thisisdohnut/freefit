# Registry Specification

## Purpose

The registry is the authoritative catalog of providers, models, endpoints, capabilities, free policies and routing metadata.

## Identity model

```text
Provider
  └── Deployment/Region
        └── Model
              └── Endpoint
```

A unique endpoint key should be deterministic:

```text
provider_id:model_id:deployment_id:region:api_mode
```

## Provider fields

```yaml
id
name
base_url
api_style
regions
free_policy_source
adapter
status
last_catalog_sync
```

## Model fields

```yaml
id
canonical_name
provider_model_id
family
parameter_count
context_window
modalities
capabilities
license
created_at
updated_at
```

## Endpoint fields

```yaml
id
provider_id
model_id
region
base_url
streaming
tool_calling
json_mode
vision
status
last_health_at
last_speed_at
last_benchmark_at
```

## Free policy

```yaml
class: F0 | F1 | F2 | F3 | F4 | UNKNOWN
is_free_now: true
quota_amount: 1000000
quota_unit: tokens
reset_at: ...
expires_at: ...
source_url: ...
verified_at: ...
```

## Status state machine

```text
UNKNOWN → DISCOVERED → VERIFIED → HEALTHY
                                   ↓
                                DEGRADED
                                   ↓
                              RATE_LIMITED
                                   ↓
                                 DOWN
                                   ↓
                              RECOVERING
                                   ↓
                                HEALTHY
```

## Registry rules

- Never delete a model simply because a provider temporarily hides it; mark it unavailable.
- Keep historical endpoint records for reproducibility.
- Preserve provider-native model IDs exactly.
- Normalize aliases separately from canonical IDs.
- Record catalog source and verification time.
