from __future__ import annotations

import time
from .core import ProbeResult
from .provider import OpenAICompatible
from .store import Store

DEFAULT_PROMPT = "Explain what an API is in about 120 words. Use plain English."


def run_probe(provider: OpenAICompatible, endpoint_id: str, model: str, store: Store, prompt: str = DEFAULT_PROMPT, max_tokens: int = 160) -> ProbeResult:
    result = provider.probe(endpoint_id, model, prompt, max_tokens=max_tokens)
    store.add_probe(result)
    return result


def bench_endpoint(provider: OpenAICompatible, endpoint_id: str, model: str, store: Store,
                   warmup: int = 1, measured: int = 5, prompt: str = DEFAULT_PROMPT) -> list[ProbeResult]:
    for _ in range(max(0, warmup)):
        provider.probe(endpoint_id, model, prompt, max_tokens=120)
    results: list[ProbeResult] = []
    for _ in range(max(1, measured)):
        results.append(run_probe(provider, endpoint_id, model, store, prompt=prompt))
        time.sleep(0.15)
    return results
