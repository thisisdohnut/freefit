from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from rich.console import Console
from rich.table import Table

from .config import load, endpoints
from .core import summarize
from .provider import OpenAICompatible
from .router import RouteRequest, choose
from .scoring import score_endpoint
from .store import Store
from .tui import run as run_tui


def providers_map(cfgs):
    return {c.name: OpenAICompatible(c) for c in cfgs}


def cmd_probe(args, store, cfgs):
    eps = [e for e in store.endpoints() if e.id == args.endpoint]
    if not eps:
        print(f"unknown endpoint: {args.endpoint}", file=sys.stderr); return 6
    ep = eps[0]; p = providers_map(cfgs).get(ep.provider)
    if not p:
        print(f"provider not configured: {ep.provider}", file=sys.stderr); return 4
    from .bench import run_probe
    r = run_probe(p, ep.id, ep.model, store, max_tokens=args.max_tokens)
    if args.json: print(json.dumps(r.to_dict(), indent=2))
    else: print(f"{ep.id}: {'PASS' if r.success else 'FAIL'} TTFT={r.ttft_ms or 0:.0f}ms TPS={r.tokens_per_second or 0:.1f} total={r.total_ms or 0:.0f}ms")
    return 0 if r.success else 5


def cmd_bench(args, store, cfgs):
    pm = providers_map(cfgs); selected = store.endpoints(free_only=args.free_only)
    if args.endpoint: selected = [e for e in selected if e.id == args.endpoint]
    from .bench import bench_endpoint
    out=[]
    for ep in selected:
        p=pm.get(ep.provider)
        if not p: continue
        rs=bench_endpoint(p,ep.id,ep.model,store,warmup=args.warmup,measured=args.runs)
        st=summarize(rs); out.append({"endpoint":ep.id,**st})
        if not args.json: print(f"{ep.id}: success={st['success_rate']*100:.0f}% TTFT p50={st['ttft_p50_ms'] or 0:.0f}ms TPS p50={st['tps_p50'] or 0:.1f}")
    if args.json: print(json.dumps(out,indent=2))
    return 0 if out else 6


def cmd_models(args, store):
    rows=[]
    for ep in store.endpoints(free_only=args.free_only):
        s=score_endpoint(ep,store.recent_probes(ep.id)); rows.append((ep,s,s['stats']))
    rows.sort(key=lambda x:x[1]['score'],reverse=True)
    if args.json:
        print(json.dumps([{"endpoint":asdict(e),"score":s['score'],"score_breakdown":s,"stats":st} for e,s,st in rows],indent=2)); return 0
    c=Console(); t=Table(title="FREEFIT ENDPOINT BOARD",expand=True)
    for col in ["STATE","MODEL","PROVIDER","FREE","SCORE","TTFT","TOK/S","P95","429"]: t.add_column(col)
    for e,s,st in rows:
        state="🟢" if s['reliability']>=95 else ("🟡" if s['reliability']>=80 else "🔴")
        t.add_row(state,e.model,e.provider,e.free_class,f"{s['score']:.1f}",f"{(st['ttft_p50_ms'] or 0)/1000:.2f}s",f"{st['tps_p50'] or 0:.0f}",f"{(st['ttft_p95_ms'] or 0)/1000:.2f}s",f"{st['429_rate']*100:.1f}%")
    c.print(t); return 0


def cmd_routes(args, store):
    req=RouteRequest(workload=args.workload,free_required=args.free_required,streaming_required=not args.no_stream,tools_required=args.tools,vision_required=args.vision,context_tokens=args.context)
    d=choose(store,req)
    payload={"workload":req.workload,"selected":asdict(d.selected) if d.selected else None,"fallbacks":[asdict(x) for x in d.fallbacks],"explanation":d.explanation}
    if args.json: print(json.dumps(payload,indent=2)); return 0 if d.selected else 6
    if not d.selected: print("No eligible route."); return 6
    print(f"SELECTED  {d.selected.provider}/{d.selected.model}")
    for x in d.explanation: print(f"  • {x}")
    print("FALLBACKS")
    for x in d.fallbacks: print(f"  → {x.provider}/{x.model}")
    return 0


def cmd_status(args,store):
    eps=store.endpoints(); out={"endpoints":len(eps),"providers":len({e.provider for e in eps}),"probes":int(store.conn.execute("select count(*) from probes").fetchone()[0])}
    print(json.dumps(out,indent=2) if args.json else f"Providers: {out['providers']}  Endpoints: {out['endpoints']}  Probe samples: {out['probes']}"); return 0


def cmd_doctor(args,cfgs,eps):
    problems=[]
    for c in cfgs:
        if not c.base_url.startswith(("https://","http://")): problems.append(f"{c.name}: invalid base_url")
        if not c.models: problems.append(f"{c.name}: no models configured")
    out={"providers":len(cfgs),"endpoints":len(eps),"problems":problems,"ok":not problems}
    print(json.dumps(out,indent=2) if args.json else ("OK: configuration looks valid" if not problems else "\n".join(problems))); return 0 if not problems else 3


def build_parser():
    p=argparse.ArgumentParser(prog="freefit",description="Free Inference Fitness & Intelligence Tracker")
    p.add_argument("--config",default="freefit.json"); p.add_argument("--db",default=".freefit/freefit.db"); p.add_argument("--json",action="store_true")
    s=p.add_subparsers(dest="cmd")
    x=s.add_parser("status"); x.add_argument("--json",action="store_true")
    x=s.add_parser("models"); x.add_argument("--json",action="store_true"); x.add_argument("--free-only",action="store_true")
    x=s.add_parser("bench"); x.add_argument("--runs",type=int,default=5); x.add_argument("--warmup",type=int,default=1); x.add_argument("--endpoint"); x.add_argument("--free-only",action="store_true"); x.add_argument("--json",action="store_true")
    x=s.add_parser("probe"); x.add_argument("endpoint"); x.add_argument("--max-tokens",type=int,default=160); x.add_argument("--json",action="store_true")
    x=s.add_parser("routes"); x.add_argument("--workload",default="chat"); x.add_argument("--free-required",action=argparse.BooleanOptionalAction,default=True); x.add_argument("--no-stream",action="store_true"); x.add_argument("--tools",action="store_true"); x.add_argument("--vision",action="store_true"); x.add_argument("--context",type=int,default=0); x.add_argument("--json",action="store_true")
    x=s.add_parser("tui"); x.add_argument("--search",default=""); x.add_argument("--sort",default="score"); x.add_argument("--refresh",type=float,default=2.0); x.add_argument("--free-only",action="store_true")
    x=s.add_parser("doctor"); x.add_argument("--json",action="store_true")
    return p


def main(argv=None):
    args=build_parser().parse_args(argv); store=Store(args.db)
    try:
        cfgs=load(args.config); eps=endpoints(cfgs)
        for e in eps: store.upsert_endpoint(e)
        if args.cmd in (None,"tui"): return run_tui(store,free_only=getattr(args,"free_only",False),search=getattr(args,"search",""),sort=getattr(args,"sort","score"),refresh=getattr(args,"refresh",2.0)) or 0
        if args.cmd=="status": return cmd_status(args,store)
        if args.cmd=="models": return cmd_models(args,store)
        if args.cmd=="probe": return cmd_probe(args,store,cfgs)
        if args.cmd=="bench": return cmd_bench(args,store,cfgs)
        if args.cmd=="routes": return cmd_routes(args,store)
        if args.cmd=="doctor": return cmd_doctor(args,cfgs,eps)
        return 2
    except KeyboardInterrupt: return 130
    finally: store.close()

if __name__=="__main__": raise SystemExit(main())
