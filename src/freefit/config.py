from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from .core import Endpoint
from .provider import ProviderConfig

DEFAULT_CONFIG = Path("freefit.json")


def load(path: str | Path = DEFAULT_CONFIG) -> list[ProviderConfig]:
    p = Path(path)
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    out: list[ProviderConfig] = []
    for item in data.get("providers", []):
        out.append(ProviderConfig(
            name=item["name"], base_url=item["base_url"], api_key_env=item.get("api_key_env", ""),
            models=list(item.get("models", [])), free_class=item.get("free_class", "UNKNOWN"),
            free_now=bool(item.get("free_now", False)), tools=bool(item.get("tools", False)),
            json_mode=bool(item.get("json_mode", False)), vision=bool(item.get("vision", False)),
            region=item.get("region", "global"), context_window=item.get("context_window"),
        ))
    return out


def endpoints(configs: list[ProviderConfig]) -> list[Endpoint]:
    out: list[Endpoint] = []
    for c in configs:
        models = c.models
        for model in models:
            eid = f"{c.name}:{model}"
            out.append(Endpoint(
                id=eid, provider=c.name, model=model, base_url=c.base_url,
                free_class=c.free_class, free_now=c.free_now, region=c.region,
                tools=c.tools, json_mode=c.json_mode, vision=c.vision,
                context_window=c.context_window,
            ))
    return out
