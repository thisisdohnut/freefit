from __future__ import annotations

from dataclasses import dataclass
from .core import Endpoint
from .scoring import score_endpoint
from .store import Store

@dataclass(slots=True)
class RouteRequest:
    workload: str = "chat"
    free_required: bool = True
    streaming_required: bool = True
    tools_required: bool = False
    vision_required: bool = False
    context_tokens: int = 0

@dataclass(slots=True)
class RouteDecision:
    selected: Endpoint | None
    fallbacks: list[Endpoint]
    explanation: list[str]


def eligible(ep: Endpoint, req: RouteRequest) -> bool:
    if req.free_required and not ep.free_now:
        return False
    if req.streaming_required and not ep.streaming:
        return False
    if req.tools_required and not ep.tools:
        return False
    if req.vision_required and not ep.vision:
        return False
    if req.context_tokens and ep.context_window and ep.context_window < req.context_tokens:
        return False
    return True


def choose(store: Store, req: RouteRequest) -> RouteDecision:
    candidates: list[tuple[Endpoint, dict]] = []
    for ep in store.endpoints(free_only=req.free_required):
        if not eligible(ep, req):
            continue
        score = score_endpoint(ep, store.recent_probes(ep.id, 30))
        if score["reliability"] < 50 and score["stats"]["samples"] > 0:
            continue
        candidates.append((ep, score))
    candidates.sort(key=lambda x: x[1]["score"], reverse=True)
    if not candidates:
        return RouteDecision(None, [], ["no eligible endpoint with acceptable live evidence"])
    selected, top = candidates[0]
    explanation = [f"highest live score {top['score']:.1f}", f"free policy {selected.free_class}", f"confidence {top['confidence']*100:.0f}%"]
    if top["stats"]["samples"] == 0:
        explanation.append("no probe samples yet; score is policy-biased and should be probed")
    return RouteDecision(selected, [x[0] for x in candidates[1:4]], explanation)
