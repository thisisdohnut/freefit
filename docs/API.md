# FREEFIT API

## Purpose

Expose registry, health, benchmark, score and routing data to terminals and agent clients.

## Endpoints

```text
GET  /api/v1/providers
GET  /api/v1/models
GET  /api/v1/endpoints
GET  /api/v1/endpoints/{id}
GET  /api/v1/endpoints/{id}/history
GET  /api/v1/health
GET  /api/v1/benchmarks
GET  /api/v1/scores
GET  /api/v1/routes?workload=coding
POST /api/v1/probe/{id}
POST /api/v1/bench
POST /api/v1/discovery/refresh
```

## Route response

```json
{
  "workload": "coding",
  "selected": {
    "endpoint": "groq/openai/gpt-oss-120b",
    "score": 97.1,
    "confidence": 0.94
  },
  "fallbacks": [
    "nvidia/nemotron-3-ultra",
    "google/gemini-flash"
  ],
  "explanation": [
    "healthy",
    "highest current coding score",
    "free policy active"
  ]
}
```

## Compatibility

The API should expose normalized concepts while preserving provider-native IDs. Future adapters can expose an OpenAI-compatible request interface without coupling the internal registry to that wire format.
