from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .config import load, endpoints
from .core import summarize
from .provider import OpenAICompatible
from .scoring import score_endpoint, rank
from .store import Store
from .tui import run as run_tui


def providers_map(cfgs):
    return {c.name: OpenAICompatible(c) for c in cfgs}


def cmd_probe(args, store, cfgs):
    eps = [e for e in store.endpoints() if e.id == args.endpoint]
    if not eps:
        print(f"unknown endpoint: {args.endpoint}", file=sys.stderr)
        return 6
    ep = eps[0]
    pm = providers_map(cfgs)
    p = pm.get(ep.provider)
    if not p:
        print(f"provider not configured: {ep.provider}", file=sys.stderr)
        return 4
    from .bench import run_probe
    r = run_probe(p, ep.id, ep.model, store, max_tokens=args.max_tokens)
    print(json.dumps(r.to_dict(), indent=2) if args.json else f"{ep.id}: {'PASS' if r.success else 'FAIL'} TTFT={r.ttft_ms:.0f}ms TPS={r.tokens_per_second or 0:.1f} total={r.total_ms:.0f}ms")
    return 0 if r.success else 5


def cmd_bench(args, store, cfgs):
    pm = providers_map(cfgs)
    selected = store.endpoints(free_only=args.free_only)
    if args.endpoint:
        selected = [e for e in selected if e.id == args.endpoint]
    from .bench import bench_endpoint
    all_results = []
    for ep in selected:
        p = pm.get(ep.provider)
        if not p:
            continue
        results = bench_endpoint(p, ep.id, ep.model, store, warmup=args.warmup, measured=args.runs)
        st = summarize(results)
        all_results.append({"endpoint": ep.id, **st})
        if not args.json:
            print(f"{ep.id}: success={st['success_rate']*100:.0f}% TTFT p50={st['ttft_p50_ms'] or 0:.0f}ms TPS p50={st['tps_p50'] or 0:.1f}")
    if args.json:
        print(json.dumps(all_results, indent=2))
    return 0 if all_results else 6


def cmd_models(args, store):
    rows = []
    for ep in store.endpoints(free_only=args.free_only):
        probes = store.recent_probes(ep.id)
        s = score_endpoint(ep, probes)
        st = s["stats"]
        rows.append((ep, s, st))
    rows.sort(key=lambda x: x[1]["score"], reverse=True)
    if args.json:
        print(json.dumps([{**e.__dict__, "score": s["score"], "stats": st} for e,s,st in rows], default=str, indent=2))
        return 0
    c = Console()
    t = Table(title="FREEFIT ENDPOINT BOARD", expand=True)
    for col in ["STATE","MODEL","PROVIDER","FREE","SCORE","TTFT","TOK/S","P95","429"]: t.add_column(col)
    for e,s,st in rows:
        state = "🟢" if s["reliability"] >= 95 else ("🟡" if s["reliability"] >= 80 else "🔴")
        t.add_row(state,e.model,e.provider,e.free_class,f"{s['score']:.1f}",
                  f"{(st['ttft_p50_ms'] or 0)/1000:.2f}s",f"{st['tps_p50'] or 0:.0f}",
                  f"{(st['ttft_p95_ms'] or 0)/1000:.2f}s",f"{st['429_rate']*100:.1f}%")
    c.print(t)
    return 0


def cmd_status(args, store):
    eps = store.endpoints()
    out = {"endpoints": len(eps), "providers": len({e.provider for e in eps}), "probes": int(store.conn.execute("select count(*) from probes").fetchone()[0])}
    print(json.dumps(out, indent=2) if args.json else f"Providers: {out['providers']}  Endpoints: {out['endpoints']}  Probe samples: {out['probes']}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="freefit", description="Free Inference Fitness & Intelligence Tracker")
    p.add_argument("--config", default="freefit.json")
    p.add_argument("--db", default=".freefit/freefit.db")
    p.add_argument("--json", action="store_true")
    p.add_argument("--free-only", action="store_true")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("status")
    sub.add_parser("models")
    b = sub.add_parser("bench"); b.add_argument("--runs", type=int, default=5); b.add_argument("--warmup", type=int, default=1); b.add_argument("--endpoint"); b.add_argument("--free-only", action="store_true")
    pr = sub.add_parser("probe"); pr.add_argument("endpoint"); pr.add_argument("--max-tokens", type=int, default=160)
    t = sub.add_parser("tui"); t.add_argument("--search", default=""); t.add_argument("--sort", default="score"); t.add_argument("--refresh", type=float, default=2.0); t.add_argument("--free-only", action="store_true")
    d = sub.add_parser("doctor")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    store = Store(args.db)
    try:
        cfgs = load(args.config)
        eps = endpoints(cfgs)
        for e in eps: store.upsert_endpoint(e)
        if args.cmd in (None, "tui"):
            return run_tui(store, free_only=getattr(args, "free_only", False), search=getattr(args, "search", ""), sort=getattr(args, "sort", "score"), refresh=getattr(args, "refresh", 2.0)) or 0
        if args.cmd == "status": return cmd_status(args, store)
        if args.cmd == "models": return cmd_models(args, store)
        if args.cmd == "probe": return cmd_probe(args, store, cfgs)
        if args.cmd == "bench": return cmd_bench(args, store, cfgs)
        if args.cmd == "doctor":
            print("FREEFIT doctor: Python/runtime OK; configured providers=%d; endpoints=%d" % (len(cfgs), len(eps)))
            return 0
        return 2
    except KeyboardInterrupt:
        return 130
    finally:
        store.close()

if __name__ == "__main__":
    raise SystemExit(main())
