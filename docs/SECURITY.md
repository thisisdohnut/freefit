# Security

## Credential policy

API keys are runtime secrets. They must never be committed to Git, registry records, benchmark artifacts or screenshots.

Recommended sources, in order:

1. OS credential store
2. environment variables
3. local ignored config file
4. interactive prompt

## Probe safety

Probes must use synthetic prompts. Production/user prompts are never benchmark data by default.

## Logging

Redact:

```text
Authorization
api_key
access_token
cookies
raw prompt content
provider secret headers
```

## Network policy

Only configured provider hosts may be contacted by automatic discovery/probing. Discovery must not turn arbitrary catalog content into an outbound URL without validation.

## Command execution

Never pass provider-returned model IDs directly to a shell command. Treat them as untrusted strings.

## Supply chain

Pin production dependencies where practical. Record version and checksum metadata in release manifests.

## Data retention

Benchmark telemetry should be minimized. Store timing/quality metrics rather than full generated content unless explicitly enabled for debugging.
