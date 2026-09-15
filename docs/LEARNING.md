# Evaluator & Learning

## Purpose

FREEFIT should improve routing decisions from observed outcomes without silently changing policy in an unsafe way.

## Evaluator

For each route attempt evaluate:

```text
request accepted?
response completed?
latency within budget?
quality acceptable?
structured output valid?
tool call valid?
fallback required?
```

## Feedback record

```yaml
route_id
endpoint_id
workload
success
quality_score
latency_score
fallback_count
user_override
created_at
```

## Learning inputs

Use aggregated evidence, not raw prompts:

- successful route rate
- benchmark quality
- latency distribution
- provider error behavior
- fallback frequency
- workload-specific preferences

## Safe learning policy

Learning can tune weights and priors, but must not bypass hard safety/policy constraints.

Recommended bounds:

```text
max weight delta per day: 5 percentage points
minimum sample count before adaptation: 30
cooldown after a policy change: 1h
```

## Exploration

Occasionally test a strong runner-up so stale assumptions can be corrected. Exploration must respect free-only, health and capability constraints.

## Rollback

Persist each scoring policy version. Any learned policy can be reverted to the previous known-good version.
