#!/usr/bin/env python3
"""
Ingestion-Hook – asynchron, deterministisch, gedächtniszentriert.

Quellen (verifiziert 2026-10-01, HTTP 200):
  - Trellis (ronsse/trellis-ai): "LLM never in the write path"; deterministische
    Klassifikatoren inline, LLM opt-in; Background-Worker für Enrichment/
    Konsolidierung; fail-soft / never-raise hook contract.
    https://github.com/ronsse/trellis-ai
  - GraphRAG-SDK (FalkorDB): Two-Step Extraction – Step 1 GLiNER (lokal, keine
    API-Calls), Step 2 LLM (verify+relations); Entity-Resolution.
    https://github.com/FalkorDB/GraphRAG-SDK
  - GLiNER-Relex: deterministische, lokale NER+RE.
    https://arxiv.org/abs/2605.10108
  - TrueMemory: SessionStart / UserPromptSubmit / SessionEnd + "encoding gate
    on each fact". https://github.com/buildingjoshbetter/TrueMemory
  - agentmemory: Lifecycle-Hooks; deterministische Dedup (SHA-256, 5min) +
    Privacy-Filter VOR dem Store. https://github.com/rohitg00/agentmemory

Lab-Prinzip: Keine Erfindungen. Mechanik = aus den Quellen; konkrete Schwellen
sind Projekt-Vorgabe (Auftrag) und als solche markiert.

Architektur:
  Write-Path (synchron, deterministisch, KEIN LLM):
      Lifecycle-Event → Dedup → Encoding-Gate → deterministische Tags → Log
  Enrichment-Path (asynchron, off the write path):
      Enrichment-Queue → Entity-Resolution → Graph-Update → Konsolidierung
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path("/home/opc/knowledge-agent")
DEFAULT_LOG = ROOT / "data/memory/tier3-working/ingestion_log.jsonl"

# --- Konfiguration (Projekt-Vorgabe = Auftrag, KEINE Quellen-Behauptung) ---
MIN_LEN = 12              # Auftrag
MAX_LEN = 8000            # Auftrag
ALLOWED_TYPES = {"prompt", "tool_result", "transcript", "note"}   # Auftrag
MIN_SOURCE_TRUST = 0.5    # Auftrag (0..1)
DEDUP_WINDOW_S = 300      # agentmemory: SHA-256, 5-min-Fenster


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# =====================================================================
# Encoding-Gate – deterministisch (Länge, Typ, Quellvertrauen). Kein LLM.
# Quelle: TrueMemory ("encoding gate on each fact"); agentmemory (Filter vor Store).
# =====================================================================
@dataclass
class GateDecision:
    accepted: bool
    reason: str


class EncodingGate:
    def __init__(self, min_len: int = MIN_LEN, max_len: int = MAX_LEN,
                 allowed: set[str] = None, min_trust: float = MIN_SOURCE_TRUST):
        self.min_len = min_len
        self.max_len = max_len
        self.allowed = allowed or set(ALLOWED_TYPES)
        self.min_trust = min_trust

    def check(self, text: str, source_type: str, source_trust: float) -> GateDecision:
        if source_type not in self.allowed:
            return GateDecision(False, f"Typ '{source_type}' nicht erlaubt")
        n = len(text or "")
        if n < self.min_len:
            return GateDecision(False, f"zu kurz ({n} < {self.min_len})")
        if n > self.max_len:
            return GateDecision(False, f"zu lang ({n} > {self.max_len})")
        if source_trust < self.min_trust:
            return GateDecision(False, f"Quellvertrauen {source_trust} < {self.min_trust}")
        return GateDecision(True, "ok")


# =====================================================================
# Enrichment-Queue – asynchron (Entity-Resolution, Graph-Update, Konsolidierung).
# Quelle: Trellis Background-Worker; GraphRAG Entity-Resolution.
# =====================================================================
class EnrichmentQueue:
    def __init__(self, log_path: Path = DEFAULT_LOG):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.processed: list[dict[str, Any]] = []
        self.log_path = log_path

    async def worker(self) -> None:
        while True:
            item = await self.queue.get()
            try:
                # Deterministische Stufen (hier als Repräsentation; kein LLM):
                item["steps"] = ["entity-resolution", "graph-update", "consolidation"]
                item["enriched_at"] = _now_iso()
                self.processed.append(item)
            except Exception:  # fail-soft (Trellis never-raise)
                pass
            finally:
                self.queue.task_done()

    async def submit(self, item: dict[str, Any]) -> None:
        await self.queue.put(item)


# =====================================================================
# Record + Hook
# =====================================================================
@dataclass
class Record:
    session_id: str
    timestamp: str
    source_type: str
    content_hash: str
    decision: str                 # session_start | accepted | rejected | session_end
    reason: str = ""
    tags: dict = field(default_factory=dict)
    enrichment: str = "skipped"   # queued | skipped


class IngestionHook:
    """Lifecycle-Hook: SessionStart, UserPromptSubmit, SessionEnd."""

    def __init__(self, gate: Optional[EncodingGate] = None,
                 queue: Optional[EnrichmentQueue] = None,
                 log_path: Path = DEFAULT_LOG):
        self.gate = gate or EncodingGate()
        self.queue = queue or EnrichmentQueue(log_path)
        self.log_path = log_path
        self._seen: dict[str, float] = {}

    # --- deterministische Tags (KEIN LLM im Write-Path) ---
    def _tags(self, session_id: str, source_type: str) -> dict:
        return {"session_id": session_id, "timestamp": _now_iso(), "source_type": source_type}

    def _is_duplicate(self, h: str) -> bool:
        now = time.time()
        self._seen = {k: v for k, v in self._seen.items() if now - v < DEDUP_WINDOW_S}
        if h in self._seen:
            return True
        self._seen[h] = now
        return False

    def _append(self, rec: Record) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")

    # --- Lifecycle-Events (fail-soft: nie in den Agent-Flow werfen) ---
    async def on_session_start(self, session_id: str, source_type: str = "note") -> Optional[Record]:
        try:
            rec = Record(session_id, _now_iso(), source_type, "", "session_start",
                         tags=self._tags(session_id, source_type), enrichment="skipped")
            self._append(rec)
            return rec
        except Exception:
            return None

    async def on_user_prompt_submit(self, session_id: str, text: str,
                                    source_type: str = "prompt",
                                    source_trust: float = 1.0) -> Optional[Record]:
        try:
            h = _sha256(text or "")
            if self._is_duplicate(h):
                rec = Record(session_id, _now_iso(), source_type, h, "rejected",
                             "Duplikat (SHA-256, 5-min-Fenster)",
                             self._tags(session_id, source_type), "skipped")
                self._append(rec)
                return rec
            d = self.gate.check(text, source_type, source_trust)
            rec = Record(session_id, _now_iso(), source_type, h,
                         "accepted" if d.accepted else "rejected", d.reason,
                         self._tags(session_id, source_type))
            if d.accepted:
                rec.enrichment = "queued"
                # Enrichment läuft ASYNCH (off the write path), kein LLM hier:
                await self.queue.submit({"session_id": session_id,
                                         "content_hash": h,
                                         "source_type": source_type})
            self._append(rec)
            return rec
        except Exception:
            return None

    async def on_session_end(self, session_id: str) -> Optional[Record]:
        try:
            rec = Record(session_id, _now_iso(), "transcript", "", "session_end",
                         tags=self._tags(session_id, "transcript"), enrichment="skipped")
            self._append(rec)
            return rec
        except Exception:
            return None


# =====================================================================
# Demo / Selbsttest
# =====================================================================
async def _demo() -> None:
    hook = IngestionHook(log_path=DEFAULT_LOG)
    worker = asyncio.create_task(hook.queue.worker())

    print("=== Ingestion-Hook Demo (deterministisch, kein LLM) ===")
    r = await hook.on_session_start("sess-001"); print("SessionStart        ->", r.decision)
    r = await hook.on_user_prompt_submit("sess-001",
        "Der Knowledge-Agent nutzt Fast Write Routing als Entscheidungsebene.",
        "prompt", 0.9); print("UserPromptSubmit OK ->", r.decision, "|", r.reason, "| enrichment:", r.enrichment)
    r = await hook.on_user_prompt_submit("sess-001", "kurz", "prompt", 0.9)
    print("Gate: zu kurz      ->", r.decision, "|", r.reason)
    r = await hook.on_user_prompt_submit("sess-001", "irgendein Inhalt", "unknown", 0.9)
    print("Gate: falscher Typ ->", r.decision, "|", r.reason)
    r = await hook.on_user_prompt_submit("sess-001",
        "Der Knowledge-Agent nutzt Fast Write Routing als Entscheidungsebene.",
        "prompt", 0.9); print("Dedup              ->", r.decision, "|", r.reason)
    r = await hook.on_user_prompt_submit("sess-001",
        "Gerücht ohne Beleg aus unsicherer Quelle.", "note", 0.2)
    print("Gate: Quellvertr.  ->", r.decision, "|", r.reason)
    r = await hook.on_session_end("sess-001"); print("SessionEnd          ->", r.decision)

    await hook.queue.queue.join()
    worker.cancel()
    print("Enrichment (async) verarbeitet:", len(hook.queue.processed), "Item(s)")
    print("Log:", hook.log_path)


if __name__ == "__main__":
    asyncio.run(_demo())
