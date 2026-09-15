# Data Model

## Entities

```text
Provider 1──N Deployment
Provider 1──N Model
Model    1──N Endpoint
Endpoint 1──N ProbeRun
Endpoint 1──N BenchmarkRun
Endpoint 1──N HealthEvent
Endpoint 1──N QuotaSnapshot
Endpoint 1──N ScoreSnapshot
Route    1──N RouteAttempt
```

## Endpoint

Core fields:

```text
id
provider_id
model_id
deployment_id
region
api_mode
status
created_at
updated_at
```

## ProbeRun

```text
id
endpoint_id
workload
started_at
first_token_at
completed_at
input_tokens
output_tokens
status_code
error_class
ttft_ms
generation_ms
total_ms
tps
```

## ScoreSnapshot

```text
endpoint_id
timestamp
quality_score
speed_score
reliability_score
free_score
freshness_score
capability_score
raw_score
confidence
final_score
explanation_json
```

## HealthEvent

Retain state changes separately from measurements so incident timelines are queryable.

## QuotaSnapshot

```text
endpoint_id
timestamp
remaining
limit
unit
reset_at
source
confidence
```

## Storage requirements

The implementation should support SQLite first for local development. The logical schema must remain portable to PostgreSQL later.

## Data integrity

- timestamps stored in UTC
- decimal metrics retain sufficient precision
- provider model IDs stored verbatim
- raw provider error payloads should be redacted before persistence
- schema version recorded with migrations
