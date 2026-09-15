# Quota & Free-Tier Tracking

## Why quota is dynamic

A provider can expose a model while changing its free allowance, rate limit, region, or limited-time promotion. FREEFIT therefore treats free status as a timestamped policy observation.

## Free classes

```text
F0  permanent/ongoing $0 inference
F1  active free quota
F2  limited-time/free promotion
F3  trial credit
F4  local/open-weight only
UNKNOWN
```

## Required fields

```yaml
free_class
is_free_now
quota_limit
quota_remaining
quota_unit
reset_at
expires_at
rpm_limit
tpm_limit
concurrency_limit
source_url
verified_at
```

## Quota pressure

```text
pressure = 1 - (remaining / limit)
```

Use provider-specific semantics when the provider publishes a different metric.

## Routing impact

Example policy:

```text
pressure < 0.70  → no penalty
0.70–0.85        → small penalty
0.85–0.95        → medium penalty
> 0.95           → strong penalty / reserve
exhausted        → ineligible
```

## Reset awareness

A quota nearly exhausted but resetting in 2 minutes is different from quota nearly exhausted for another 24 hours. The router should incorporate `time_to_reset` where known.

## Verification

Free policy source URLs and verification timestamps must be stored. Never infer permanent free status from a temporary promotion.
