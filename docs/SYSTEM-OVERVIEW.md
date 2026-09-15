# System Overview

FREEFIT is a live decision system for free/free-tier LLM inference.

## Problem

Provider catalogs tell us what exists, but not necessarily what is fast, healthy or usable right now. Free allocations also change over time.

## Outputs

FREEFIT produces three classes of output:

### Observations

Facts measured or discovered:

- model exists
- endpoint responds
- TTFT
- TPS
- errors
- quota
- capabilities
- free policy

### Assessments

Derived state:

- health
- confidence
- score
- degradation
- route eligibility

### Decisions

Actions:

- select endpoint
- retry
- fallback
- open circuit
- refresh catalog
- schedule probe

## Source-of-truth rule

The registry owns identity. Providers own their native state. Probes own measured performance. The scoring engine owns derived ranking. The router owns request-specific decisions.

No component should overwrite another component's domain without an explicit contract.

## Operational loop

```text
observe → normalize → store → score → decide → execute → evaluate → learn
```
