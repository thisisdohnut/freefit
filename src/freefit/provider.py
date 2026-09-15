from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from typing import Callable

from .core import ProbeResult, classify_http, estimate_tokens, now_iso


@dataclass(slots=True)
class ProviderConfig:
    name: str
    base_url: str
    api_key_env: str
    models: list[str]
    free_class: str = "UNKNOWN"
    free_now: bool = False
    tools: bool = False
    json_mode: bool = False
    vision: bool = False
    region: str = "global"
    context_window: int | None = None


class OpenAICompatible:
    def __init__(self, cfg: ProviderConfig, timeout: float = 60.0):
        self.cfg = cfg
        self.timeout = timeout

    @property
    def api_key(self) -> str | None:
        return os.getenv(self.cfg.api_key_env) if self.cfg.api_key_env else None

    def headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "text/event-stream"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def probe(self, endpoint_id: str, model: str, prompt: str, max_tokens: int = 160) -> ProbeResult:
        start_iso = now_iso()
        t0 = time.perf_counter()
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        req = urllib.request.Request(
            self.cfg.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=self.headers(),
            method="POST",
        )
        first = None
        text_parts: list[str] = []
        usage_output: int | None = None
        status = None
        request_id = str(uuid.uuid4())
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                status = resp.status
                for raw in resp:
                    if first is None:
                        first = time.perf_counter()
                    line = raw.decode("utf-8", "ignore").strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        continue
                    try:
                        obj = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    rid = obj.get("id")
                    if rid:
                        request_id = str(rid)
                    usage = obj.get("usage") or {}
                    if isinstance(usage.get("completion_tokens"), int):
                        usage_output = usage["completion_tokens"]
                    choices = obj.get("choices") or []
                    if choices:
                        delta = (choices[0] or {}).get("delta") or {}
                        content = delta.get("content")
                        if isinstance(content, str):
                            text_parts.append(content)
            t1 = time.perf_counter()
            output_tokens = usage_output or estimate_tokens("".join(text_parts))
            generation_ms = ((t1 - first) * 1000) if first else None
            ttft_ms = ((first - t0) * 1000) if first else None
            total_ms = (t1 - t0) * 1000
            tps = (output_tokens / (generation_ms / 1000)) if generation_ms and output_tokens else None
            return ProbeResult(endpoint_id, start_iso, now_iso(), ttft_ms, generation_ms, total_ms,
                               output_tokens, tps, status, True, request_id=request_id,
                               estimated_tokens=usage_output is None)
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "ignore")[:500]
            except Exception:
                pass
            return ProbeResult(endpoint_id, start_iso, now_iso(), None, None,
                               (time.perf_counter() - t0) * 1000, 0, None, e.code, False,
                               classify_http(e.code), body, request_id=request_id)
        except TimeoutError as e:
            return ProbeResult(endpoint_id, start_iso, now_iso(), None, None,
                               (time.perf_counter() - t0) * 1000, 0, None, None, False,
                               "TIMEOUT", str(e), request_id=request_id)
        except Exception as e:
            return ProbeResult(endpoint_id, start_iso, now_iso(), None, None,
                               (time.perf_counter() - t0) * 1000, 0, None, None, False,
                               "NETWORK", str(e)[:500], request_id=request_id)

    def list_models(self) -> list[str]:
        if self.cfg.models:
            return self.cfg.models
        req = urllib.request.Request(self.cfg.base_url.rstrip("/") + "/models", headers=self.headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return [str(x["id"]) for x in data.get("data", []) if isinstance(x, dict) and x.get("id")]
        except Exception:
            return []
