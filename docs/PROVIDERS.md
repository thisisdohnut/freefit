# Provider Adapter Contract

## Purpose

Provider adapters isolate authentication, endpoint discovery, request shape, streaming semantics, token accounting and error normalization.

## Required interface

```text
list_models()
get_model(model_id)
get_free_policy(model_id)
probe(endpoint, request)
stream(endpoint, request)
normalize_error(error)
get_quota()
get_rate_limits()
```

## Adapter output normalization

All providers emit a common internal response:

```yaml
provider
model
endpoint
request_id
started_at
first_token_at
completed_at
input_tokens
output_tokens
status_code
finish_reason
error_code
error_class
rate_limit
quota
```

## Error classes

```text
AUTH
NOT_FOUND
INVALID_REQUEST
RATE_LIMITED
QUOTA_EXHAUSTED
SERVER_ERROR
TIMEOUT
NETWORK
CONTENT_FILTER
UNKNOWN
```

## Provider isolation

A failing adapter must return a structured error and never crash the scheduler or router.

## Credential handling

Adapters receive secrets at runtime. Credentials never belong in the registry, benchmark output, logs or committed files.

## Regional awareness

Where provider behavior is regional, treat region as part of endpoint identity and benchmark key.
