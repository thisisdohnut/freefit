# FREEFIT TUI / Graphics Specification

## Design objective

Build a terminal interface that is as information-dense as llmfit, but optimized for **live cloud inference operations**.

The interface should feel like an **LLM network observatory**, not a static catalog.

## Main screen: Command Center

```text
╭──────────────────────────────────────────────────────────────────────────────╮
│ FREEFIT  •  COMMAND CENTER                              LIVE ●  21:42 MYT    │
├──────────────────────────────────────────────────────────────────────────────┤
│ Providers  11 │ Endpoints 84 │ Healthy 61 │ Degraded 12 │ Down 3 │ Stale 8 │
├──────────────────────────────────────────────────────────────────────────────┤
│ TOP FREE ROUTES                                                             │
│                                                                            │
│  MODEL                 PROVIDER       SCORE  TTFT    TOK/S   429   STATE  │
│  GPT-OSS 120B          Groq            97    0.19s   412    0.3%  🟢    │
│  Gemini Flash           Google          94    0.34s   181    0.5%  🟢    │
│  Nemotron 3 Ultra      NVIDIA          91    0.52s   121    0.2%  🟢    │
│  Ling Flash Fin         OpenRouter      83    0.68s   105    3.1%  🟡    │
├──────────────────────────────────────────────────────────────────────────────┤
│ LIVE SIGNALS                                                               │
│ TTFT  ▂▂▃▃▅▇█▆▄▃       TPS  █▇▇▆▄▂▂▃▅▆       ERR ▁▁▁▂▂▃▄▆▅▃              │
│       0.31 → 1.18 s           182 → 104            0.2 → 3.1 %             │
├──────────────────────────────────────────────────────────────────────────────┤
│ ROUTER: coding → Groq / GPT-OSS 120B ●                                    │
│         fallback → NVIDIA / Nemotron 3 Ultra ●                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ [/] search  [f] filters  [s] sort  [m] compare  [b] bench  [r] routes     │
│ [p] providers  [o] observatory  [d] detail  [q] quit                        │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Primary visual primitives

### 1. Status pills

```text
🟢 HEALTHY
🟡 DEGRADED
🔴 DOWN
🔵 PROBING
⚪ STALE
🟣 QUOTA
```

### 2. Micro-bars

Use Unicode blocks to show normalized values in a tiny footprint:

```text
TTFT  ███████░░░  0.74s
TPS   █████████░  144/s
ERROR █░░░░░░░░░  0.4%
```

### 3. Sparklines

Every detail view should show a short rolling window without requiring a full chart:

```text
last 30 samples
▁▁▂▃▃▂▄▆█▇▆▅▄▃▂▂▁▂▃▅▆▅▄▃▃▂
```

### 4. Health heatmap

Endpoint matrix:

```text
                 5m   30m   6h   24h
Groq              🟢    🟢    🟢    🟢
Google            🟢    🟢    🟡    🟢
NVIDIA            🟢    🟡    🟡    🟢
OpenRouter        🟡    🟡    🟢    🟢
OpenCode Zen      🔴    🟡    🟡    🟢
```

### 5. Latency ladder

Use a horizontal normalized bar for direct comparison:

```text
0ms                         2s
Groq       ███                 0.19s
Google     █████               0.34s
NVIDIA     ████████            0.52s
Router     ███████████         0.81s
```

### 6. Confidence marker

Scores must expose confidence:

```text
97.4 ✓ HIGH
89.2 ~ MEDIUM
72.1 ? LOW
```

## Model Board

The default table should preserve llmfit-style density while changing columns to:

```text
STATE MODEL PROVIDER FREE SCORE TTFT TOK/S P95 ERR QUOTA AGE CAP
```

Recommended compact form:

```text
🟢 GPT-OSS 120B  Groq       F0  97  0.19  412  0.41  0.3%  88%  2m  C/T
🟢 Gemini Flash   Google     F1  94  0.34  181  0.62  0.5%  71%  4m  C/V/T
🟡 Nemotron      OpenRouter F0  83  0.81   93  1.54  2.4%  54%  1m  C/T
```

## Detail screen

```text
MODEL DETAIL
────────────────────────────────────
GPT-OSS 120B
Provider       Groq
Free class     F0
Capabilities   coding / tools / json

LIVE PERFORMANCE
TTFT           0.19s    ███
P50 TTFT       0.18s
P95 TTFT       0.41s
TOK/S          412      ██████████
P95 TOK/S      351
TOTAL          0.53s

RELIABILITY
Success        99.7%
429            0.3%
Timeout        0.0%

TREND (30 samples)
TTFT  ▂▂▃▃▂▁▂▃▄▅▆▄▃▂▁
TOK/S █████▇▆▅▆▇█████▇

ROUTER
Coding         #1
JSON           #2
Reasoning      #3
Fallback       NVIDIA / Nemotron 3 Ultra
```

## Compare screen

Columns are endpoints, rows are metrics. Best values receive a marker.

```text
                     Groq        Google      NVIDIA
──────────────────────────────────────────────────────
Score                 97          94          91
TTFT                  0.19s       0.34s       0.52s
TOK/S                 412         181         121
P95 TTFT              0.41s       0.62s       0.81s
Error                  0.3%        0.5%        0.2%   ← reliability winner
Quota                  88%         71%         64%
Freshness              2m          4m          1m
```

## Observatory

The observatory is the major visual differentiator from a static model browser.

```text
FREEFIT OBSERVATORY

TTFT     ▂▂▂▃▄▅▆█▇▅▄▃▂▂
TOK/S    █████▇▆▄▃▂▃▅▆██
429      ▁▁▁▁▂▂▃▄▆█▇▅▃▂

EVENTS
13:21  🟡 OpenRouter latency regression
13:34  🔴 OpenCode Zen 429 spike
13:46  🟢 OpenRouter recovered
```

## Theme philosophy

Support dark and light themes, but keep semantics independent of specific colors. Color must reinforce status rather than carry meaning alone.

## Accessibility

Every graphical state needs a text equivalent. Examples:

```text
🟢 = HEALTHY
████ = high
···· = low
```

The UI must remain understandable on terminals with poor Unicode/color support.
