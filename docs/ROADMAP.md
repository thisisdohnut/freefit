# FREEFIT Roadmap

## Phase 0 — Documentation foundation

- product scope
- architecture
- registry contract
- provider adapter contract
- metrics
- benchmark methodology
- scoring
- routing
- fallback
- TUI specification
- security/testing

## Phase 1 — Local control plane

Deliver:

- SQLite store
- static provider registry
- provider adapter interface
- health probes
- speed probes
- first TUI model board
- JSON export

## Phase 2 — Live discovery

Deliver:

- catalog discovery scheduler
- provider/model diffing
- free-policy verification
- quota snapshots
- stale-state handling

## Phase 3 — Benchmark engine

Deliver:

- standard workload suite
- percentile statistics
- benchmark history
- concurrency controls
- benchmark cache
- repeatable fixtures

## Phase 4 — Router

Deliver:

- request classifier
- hard constraints
- scoring integration
- route explanations
- fallback chains
- circuit breakers

## Phase 5 — Observatory

Deliver:

- sparklines
- heatmaps
- incident timeline
- provider health board
- trend-aware scores
- degradation alerts

## Phase 6 — Learning

Deliver:

- outcome evaluator
- route success feedback
- adaptive weights
- exploration vs exploitation policy
- automatic calibration

## Phase 7 — Ecosystem integration

Targets:

- Kimi Code
- Hermes-Agent
- OpenCode-compatible clients
- generic OpenAI-compatible consumers
- REST API

## Definition of done for v1

A user can run one command, see all discovered free/free-tier endpoints, understand which are fast/slow, run a benchmark, inspect the evidence behind each score, route a workload to the best healthy endpoint, and automatically fail over when conditions change.
