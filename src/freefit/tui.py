from __future__ import annotations

import time
from datetime import datetime, timezone
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress_bar import ProgressBar
from rich.columns import Columns

from .core import summarize
from .scoring import score_endpoint
from .store import Store

SPARK = "▁▂▃▄▅▆▇█"


def sparkline(values: list[float]) -> str:
    if not values:
        return "·"
    lo, hi = min(values), max(values)
    if hi == lo:
        return SPARK[3] * len(values)
    return "".join(SPARK[min(7, int((v - lo) / (hi - lo) * 7))] for v in values)


def render(store: Store, free_only: bool = False, search: str = "", sort: str = "score"):
    endpoints = store.endpoints(free_only=free_only)
    rows = []
    for ep in endpoints:
        if search and search.lower() not in f"{ep.provider} {ep.model}".lower():
            continue
        probes = store.recent_probes(ep.id, 30)
        score = score_endpoint(ep, probes)
        rows.append((ep, score, probes))
    rows.sort(key=lambda x: x[1].get(sort, 0) if sort in x[1] else x[1].get("score", 0), reverse=True)

    healthy = sum(1 for _, s, _ in rows if s["reliability"] >= 95)
    degraded = len(rows) - healthy
    title = Text("FREEFIT  •  LIVE INFERENCE OBSERVATORY", style="bold cyan")
    stats = Text(f" Endpoints {len(rows)}  │  Healthy {healthy}  │  Degraded {degraded}  │  Updated {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")

    t = Table(expand=True, box=None, padding=(0, 1), show_header=True)
    for h in ["STATE", "MODEL", "PROVIDER", "FREE", "SCORE", "TTFT", "TOK/S", "P95", "429", "CONF"]:
        t.add_column(h, no_wrap=True)
    for ep, s, probes in rows[:40]:
        st = "🟢" if s["reliability"] >= 95 else ("🟡" if s["reliability"] >= 80 else "🔴")
        stt = summarize(probes)
        ttft = stt.get("ttft_p50_ms")
        tps = stt.get("tps_p50")
        p95 = stt.get("ttft_p95_ms")
        vals = [
            st, ep.model[:28], ep.provider[:14], ep.free_class,
            f"{s['score']:5.1f}", f"{ttft/1000:.2f}s" if ttft else "—",
            f"{tps:.0f}" if tps else "—", f"{p95/1000:.2f}s" if p95 else "—",
            f"{stt.get('429_rate',0)*100:.1f}%", f"{s['confidence']*100:.0f}%",
        ]
        t.add_row(*vals)

    signals = []
    for ep, _, probes in rows[:5]:
        ttfts = [r.ttft_ms for r in reversed(probes) if r.ttft_ms]
        tpss = [r.tokens_per_second for r in reversed(probes) if r.tokens_per_second]
        signals.append(f"{ep.provider}/{ep.model[:16]}  TTFT {sparkline(ttfts[-18:])}  TPS {sparkline(tpss[-18:])}")
    body = Group(title, stats, Panel(t, border_style="cyan"), Panel(Text("\n".join(signals) or "No measurements yet"), title="LIVE SIGNALS", border_style="blue"))
    return body


def run(store: Store, free_only: bool = False, search: str = "", sort: str = "score", refresh: float = 2.0):
    console = Console()
    with Live(render(store, free_only, search, sort), console=console, refresh_per_second=2, screen=False) as live:
        while True:
            time.sleep(max(0.25, refresh))
            live.update(render(store, free_only, search, sort))
