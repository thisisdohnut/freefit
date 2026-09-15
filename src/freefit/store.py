from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .core import Endpoint, ProbeResult, now_iso

SCHEMA = """
CREATE TABLE IF NOT EXISTS endpoints (
  id TEXT PRIMARY KEY,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  base_url TEXT NOT NULL,
  api_style TEXT NOT NULL,
  free_class TEXT NOT NULL,
  free_now INTEGER NOT NULL DEFAULT 0,
  region TEXT NOT NULL,
  streaming INTEGER NOT NULL DEFAULT 1,
  tools INTEGER NOT NULL DEFAULT 0,
  json_mode INTEGER NOT NULL DEFAULT 0,
  vision INTEGER NOT NULL DEFAULT 0,
  context_window INTEGER,
  enabled INTEGER NOT NULL DEFAULT 1,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS probes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  endpoint_id TEXT NOT NULL,
  started_at TEXT NOT NULL,
  completed_at TEXT NOT NULL,
  ttft_ms REAL,
  generation_ms REAL,
  total_ms REAL,
  output_tokens INTEGER NOT NULL,
  tps REAL,
  status_code INTEGER,
  success INTEGER NOT NULL,
  error_class TEXT,
  error_message TEXT,
  estimated_tokens INTEGER NOT NULL DEFAULT 0,
  request_id TEXT,
  FOREIGN KEY(endpoint_id) REFERENCES endpoints(id)
);
CREATE INDEX IF NOT EXISTS idx_probes_endpoint_time ON probes(endpoint_id, completed_at DESC);
CREATE TABLE IF NOT EXISTS scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  endpoint_id TEXT NOT NULL,
  measured_at TEXT NOT NULL,
  score REAL NOT NULL,
  speed REAL NOT NULL,
  reliability REAL NOT NULL,
  free_value REAL NOT NULL,
  freshness REAL NOT NULL,
  confidence REAL NOT NULL,
  explanation TEXT NOT NULL,
  FOREIGN KEY(endpoint_id) REFERENCES endpoints(id)
);
"""


class Store:
    def __init__(self, path: str | Path = ".freefit/freefit.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def upsert_endpoint(self, e: Endpoint) -> None:
        self.conn.execute(
            """INSERT INTO endpoints VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
              provider=excluded.provider, model=excluded.model, base_url=excluded.base_url,
              api_style=excluded.api_style, free_class=excluded.free_class, free_now=excluded.free_now,
              region=excluded.region, streaming=excluded.streaming, tools=excluded.tools,
              json_mode=excluded.json_mode, vision=excluded.vision, context_window=excluded.context_window,
              enabled=excluded.enabled, updated_at=excluded.updated_at""",
            (
                e.id, e.provider, e.model, e.base_url, e.api_style, e.free_class, int(e.free_now), e.region,
                int(e.streaming), int(e.tools), int(e.json_mode), int(e.vision), e.context_window,
                int(e.enabled), now_iso(),
            ),
        )
        self.conn.commit()

    def upsert_many(self, endpoints: Iterable[Endpoint]) -> None:
        for e in endpoints:
            self.upsert_endpoint(e)

    def endpoints(self, free_only: bool = False) -> list[Endpoint]:
        q = "SELECT * FROM endpoints WHERE enabled=1"
        args: list[object] = []
        if free_only:
            q += " AND free_now=1"
        q += " ORDER BY provider, model"
        rows = self.conn.execute(q, args).fetchall()
        return [Endpoint(**{
            "id": r["id"], "provider": r["provider"], "model": r["model"],
            "base_url": r["base_url"], "api_style": r["api_style"],
            "free_class": r["free_class"], "free_now": bool(r["free_now"]),
            "region": r["region"], "streaming": bool(r["streaming"]),
            "tools": bool(r["tools"]), "json_mode": bool(r["json_mode"]),
            "vision": bool(r["vision"]), "context_window": r["context_window"],
            "enabled": bool(r["enabled"]),
        }) for r in rows]

    def add_probe(self, r: ProbeResult) -> None:
        self.conn.execute(
            """INSERT INTO probes(endpoint_id,started_at,completed_at,ttft_ms,generation_ms,total_ms,
            output_tokens,tps,status_code,success,error_class,error_message,estimated_tokens,request_id)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (r.endpoint_id, r.started_at, r.completed_at, r.ttft_ms, r.generation_ms, r.total_ms,
             r.output_tokens, r.tokens_per_second, r.status_code, int(r.success), r.error_class,
             r.error_message, int(r.estimated_tokens), r.request_id),
        )
        self.conn.commit()

    def recent_probes(self, endpoint_id: str, limit: int = 30) -> list[ProbeResult]:
        rows = self.conn.execute(
            "SELECT * FROM probes WHERE endpoint_id=? ORDER BY completed_at DESC LIMIT ?",
            (endpoint_id, limit),
        ).fetchall()
        return [ProbeResult(
            endpoint_id=r["endpoint_id"], started_at=r["started_at"], completed_at=r["completed_at"],
            ttft_ms=r["ttft_ms"], generation_ms=r["generation_ms"], total_ms=r["total_ms"],
            output_tokens=r["output_tokens"], tokens_per_second=r["tps"], status_code=r["status_code"],
            success=bool(r["success"]), error_class=r["error_class"], error_message=r["error_message"],
            estimated_tokens=bool(r["estimated_tokens"]), request_id=r["request_id"],
        ) for r in rows]

    def latest_score(self, endpoint_id: str):
        return self.conn.execute(
            "SELECT * FROM scores WHERE endpoint_id=? ORDER BY measured_at DESC LIMIT 1", (endpoint_id,)
        ).fetchone()

    def save_score(self, endpoint_id: str, score: dict) -> None:
        self.conn.execute(
            "INSERT INTO scores(endpoint_id,measured_at,score,speed,reliability,free_value,freshness,confidence,explanation) VALUES(?,?,?,?,?,?,?,?,?)",
            (endpoint_id, score["measured_at"], score["score"], score["speed"], score["reliability"],
             score["free_value"], score["freshness"], score["confidence"], json.dumps(score["explanation"])),
        )
        self.conn.commit()
