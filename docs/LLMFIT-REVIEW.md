# LLMFIT Review → FREEFIT Design Direction

## Executive summary

[llmfit](https://github.com/AlexsJones/llmfit) has a strong terminal-first information design: it puts machine specs and a dense model table on screen, supports search/filter/sort, selection and comparison, community benchmark data, and a live inference benchmark view. Its current documentation describes columns such as score, estimated/measured tok/s, fit, memory, parameters, context, quantization and use case; it also has a community leaderboard with tok/s, TTFT and VRAM and an inference bench with TTFT, TPS and total latency. See the [TUI guide](https://github.com/AlexsJones/llmfit/blob/main/docs/tui.md).

FREEFIT should preserve the **information density and keyboard efficiency** while changing the object of analysis from **model × local hardware** to **endpoint × provider × current network/service conditions**.

## What llmfit gets right

### 1. Dense primary table

The main view answers many questions without opening a detail page. This is exactly right for FREEFIT.

### 2. Search, filtering and sorting

Users can narrow a large catalog quickly. FREEFIT needs the same interaction model, but with provider, free-status, health, capability and latency filters.

### 3. Compare view

Side-by-side comparison turns a model list into a decision tool. FREEFIT should extend this to compare **endpoints**, not only model families.

### 4. Community measurements

llmfit makes a useful distinction between estimates and measured/community results. FREEFIT should make that distinction even stricter because cloud endpoint performance changes over time.

### 5. Dedicated benchmark surfaces

The separation between the model browser, community leaderboard and live benchmark is a strong pattern. FREEFIT should keep this separation but connect them through one score/history system.

## What FREEFIT should improve

### A. Make time first-class

Every speed number needs:

```text
value
sample_count
measured_at
window
region
network
confidence
source
```

### B. Show provider variance

Instead of:

```text
Nemotron 3 Ultra → 118 tok/s
```

show:

```text
Nemotron 3 Ultra
NVIDIA       121 tok/s   🟢
OpenRouter    92 tok/s   🟡
```

The endpoint is the routing unit.

### C. Show trends, not only snapshots

Use compact sparklines:

```text
TTFT  ▂▂▃▃▅▇█▆▄▃   0.31 → 1.18s
TPS   █▇▇▆▄▂▂▃▅▆   182 → 104
```

### D. Explain why a score changed

A user should be able to see:

```text
LIVE SCORE 91 → 74

Reason:
  TTFT P95       +81%
  429 rate       +4.2pp
  quota          23% remaining
```

### E. Add an explicit free-state indicator

`FREE=true` is insufficient. FREEFIT uses:

```text
F0  permanent $0 inference
F1  active free quota
F2  limited-time free
F3  trial credit
F4  local/open-weight only
DEGRADED / EXPIRED / UNKNOWN
```

## FREEFIT visual language

llmfit's table uses compact terminal colors, badges, selected-row highlighting and status indicators. FREEFIT keeps the terminal-native philosophy but introduces a visual hierarchy based on operational state:

```text
🟢 HEALTHY     endpoint healthy and within policy
🟡 DEGRADED    latency/error/queue regression
🔴 DOWN        request failures or timeout threshold exceeded
🔵 PROBING     benchmark/health request currently running
⚪ STALE       observation older than freshness window
🟣 QUOTA       quota/rate-limit constrained
```

## Proposed FREEFIT screens

```text
1. COMMAND CENTER
   provider health + top models + live rankings

2. ENDPOINT BOARD
   dense table; default power-user screen

3. MODEL DETAIL
   metrics + history + capability + route recommendation

4. PROVIDER DETAIL
   provider health, quota, rate-limit and endpoint matrix

5. COMPARE
   endpoints side-by-side

6. OBSERVATORY
   time-series / sparklines / degradation events

7. ROUTING MATRIX
   task profile × endpoint score

8. BENCH LAB
   run controlled benchmark suite
```

## Key design rule

Do not make the UI pretty at the cost of decision speed.

Target interaction:

```text
launch → understand in 2 seconds
find model → < 5 seconds
compare 2–5 endpoints → < 10 seconds
identify degraded provider → one glance
select best endpoint → one keypress
```

## Reference

- [llmfit repository](https://github.com/AlexsJones/llmfit)
- [llmfit TUI guide](https://github.com/AlexsJones/llmfit/blob/main/docs/tui.md)
- [llmfit benchmarking guide](https://github.com/AlexsJones/llmfit/blob/main/docs/benchmarking.md)
