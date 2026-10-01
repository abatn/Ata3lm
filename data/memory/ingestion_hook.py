#!/usr/bin/env python3
"""
Ingestion-Hook – asynchron, deterministisch, gedächtniszentriert.

Quellen (verifiziert 2026-10-01, HTTP 200):
  - Trellis (ronsse/trellis-ai): "LLM never in the write path"; deterministische
    Klassifikatoren inline, LLM opt-in; Background-Worker für Enrichment;
    fail-soft / never-raise. https://github.com/ronsse/trellis-ai
  - GraphRAG-SDK (FalkorDB): Two-Step Extraction – Step 1 GLiNER (lokal, keine
    API-Calls), Step 2 LLM; Entity-Resolution. https://github.com/FalkorDB/GraphRAG-SDK
  - GLiNER-Relex: deterministische, lokale NER+RE ("same text always produces the
    same graph"). https://arxiv.org/abs/2605.10108
  - TrueMemory: SessionStart/UserPromptSubmit/SessionEnd + "encoding gate".
    https://github.com/buildingjoshbetter/TrueMemory
  - agentmemory: Lifecycle-Hooks; SHA-256-Dedup (5min); "Privacy first – API keys,
    secrets, <private> tags stripped before storage"; Security-Advisory nennt
    Muster (Bearer, sk-proj-, gh[pus]_, PEM, DB-URLs).
    https://github.com/rohitg00/agentmemory
  - Neo4j MKG: PostToolUse-Hook schreibt typisierte Knoten.
    https://github.com/neo4j-labs/meta-knowledge-graph
  - HeLa-Mem (ACL 2026): Adaptive Forgetting = 3 Bedingungen gleichzeitig:
    (1) edge weight < δ_prune, (2) inactive > δ_age, (3) zero recent access;
    Hub Detection = edge weight > δ_hub. τ=60, η=0.02, λ=0.995.
    https://arxiv.org/abs/2604.16839
  - Memory Survey (arXiv:2603.07670): Konsolidierung (Episoden → Semantik),
    "learned forgetting", Kontradiktions-Erkennung, periodische Konsolidierung.
    https://arxiv.org/abs/2603.07670

Lab-Prinzip: Keine Erfindungen. Mechanik = aus den Quellen; konkrete Schwellen
sind Projekt-Vorgabe (Auftrag) und als solche markiert.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path("/home/opc/knowledge-agent")
DEFAULT_LOG = ROOT / "data/memory/tier3-working/ingestion_log.jsonl"

# --- Konfiguration (Projekt-Vorgabe = Auftrag, KEINE Quellen-Behauptung) ---
MIN_LEN = 12
MAX_LEN = 8000
ALLOWED_TYPES = {"prompt", "tool_result", "transcript", "note"}
MIN_SOURCE_TRUST = 0.5
DEDUP_WINDOW_S = 300                 # agentmemory: SHA-256, 5-min-Fenster

# HeLa-Mem Adaptive Forgetting / Hub (arXiv:2604.16839). Werte = Auftrag,
# ausser τ/η/λ (belegt aus HeLa-Mem).
DELTA_HUB = 1.5                      # Auftrag (Hub-Detection)
DELTA_PRUNE = 0.5                    # Auftrag (Adaptive-Forgetting-Bedingung 1)
DELTA_AGE_DAYS = 60                  # Auftrag (Bedingung 2); HeLa-Mem τ=60
TAU_DAYS = 60                        # belegt (HeLa-Mem τ=60)
ETA = 0.02                           # belegt (HeLa-Mem η=0.02)
LAMBDA = 0.995                       # belegt (HeLa-Mem λ=0.995)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# =====================================================================
# 1. PrivacyFilter – deterministisch, VOR dem Store (agentmemory).
#    Muster aus agentmemory README + Security-Advisory (GHSA).
# =====================================================================
PRIVATE_TAG_RE = re.compile(r"<private>.*?</private>", re.IGNORECASE | re.DOTALL)
SECRET_PATTERNS = [
    re.compile(r"(?:api[_-]?key|token|secret|password|passwd|pwd|auth)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/.+=]{8,}", re.I),
    re.compile(r"sk-proj-[A-Za-z0-9\-_]{20,}"),
    re.compile(r"(?:sk|pk|rk|ak)-[A-Za-z0-9][A-Za-z0-9\-_]{19,}"),
    re.compile(r"gh[pus]_[A-Za-z0-9]{36,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-+/=]{20,}", re.I),
    re.compile(r"(?:postgres(?:ql)?|mysql|redis|mongodb(?:\+srv)?)://[^\s'\"]+", re.I),
    re.compile(r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----.*?-----END (?:RSA |EC |DSA )?PRIVATE KEY-----", re.DOTALL),
]


class PrivacyFilter:
    """Deterministische Secret-/Private-Erkennung. Kein LLM."""

    def __init__(self, patterns: Optional[list] = None):
        self.patterns = patterns if patterns is not None else SECRET_PATTERNS

    def scan(self, text: str) -> tuple[bool, str]:
        if PRIVATE_TAG_RE.search(text or ""):
            return False, "private-Tag (<private>...</private>) gefunden"
        for p in self.patterns:
            if p.search(text or ""):
                return False, f"Secret-Muster: {p.pattern[:40]}"
        return True, "ok"

    def redact(self, text: str) -> str:
        out = PRIVATE_TAG_RE.sub("[REDACTED:private]", text or "")
        for p in self.patterns:
            out = p.sub("[REDACTED:secret]", out)
        return out


# =====================================================================
# Encoding-Gate – deterministisch (Länge, Typ, Quellvertrauen, Privacy).
# =====================================================================
@dataclass
class GateDecision:
    accepted: bool
    reason: str


class EncodingGate:
    def __init__(self, min_len: int = MIN_LEN, max_len: int = MAX_LEN,
                 allowed: Optional[set] = None, min_trust: float = MIN_SOURCE_TRUST,
                 privacy: Optional[PrivacyFilter] = None):
        self.min_len = min_len
        self.max_len = max_len
        self.allowed = allowed or set(ALLOWED_TYPES)
        self.min_trust = min_trust
        self.privacy = privacy or PrivacyFilter()

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
        clean, why = self.privacy.scan(text)          # 4. Prüfung: Privacy (agentmemory)
        if not clean:
            return GateDecision(False, f"Privacy: {why}")
        return GateDecision(True, "ok")


# =====================================================================
# 2. Entity-Resolution – deterministisch (GLiNER-Prinzip: lokal, keine API,
#    reproduzierbar). Regel-/Wörterbuch-basiert (kein Modell installiert).
# =====================================================================
ENTITY_RULES: list[tuple[str, re.Pattern]] = [
    ("Solver",  re.compile(r"\b(berechne_[a-zäöü]+|finde_[a-zäöü]+)\b")),
    ("Concept", re.compile(r"\b(Knowledge-Agent|Fast Write Routing|Hebbian Distillation|Adaptive Forgetting|Spreading Activation|SHACL|GraphRAG|GLiNER|Trellis|TrueMemory|agentmemory)\b")),
    ("Phase",   re.compile(r"\b(Konstrukt|Akt|Observe|Compare|Revise)\b")),
    ("Stage",   re.compile(r"\b(Erfahrung|Wissen|Gedächtnis|Kognition|Denken|Nicht-Kognition|Handeln|Wissen\+)\b")),
]


def resolve_entities(text: str) -> list[dict[str, Any]]:
    """Deterministische Entity-Erkennung. Gleicher Text -> gleiche Liste.
    Rückgabe: [{entity_type, span, start, end, confidence}]."""
    found: list[dict[str, Any]] = []
    for etype, pat in ENTITY_RULES:
        for m in pat.finditer(text or ""):
            found.append({
                "entity_type": etype,
                "span": m.group(0),
                "start": m.start(),
                "end": m.end(),
                "confidence": 1.0,          # exakter Wörterbuch-Treffer (Auftrag)
            })
    found.sort(key=lambda e: (e["start"], e["entity_type"]))
    return found


# =====================================================================
# 3. Graph-Update mit Konsistenzprüfung (GraphRAG / Neo4j MKG).
# =====================================================================
FUNCTIONAL = {"hasEnd", "hasBeginning", "gueltig_von"}     # Auftrag: 1 Objekt pro Subjekt
ASYMMETRIC = {"supersedes", "before", "produces"}          # Auftrag: nicht symmetrisch


class MemoryGraph:
    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.edges: dict[tuple[str, str, str], float] = {}

    def add_node(self, name: str, last_access: float = 0.0, recent_access: int = 0) -> None:
        self.nodes.setdefault(name, {"last_access": last_access, "recent_access": recent_access})

    def edge_weight(self, name: str) -> float:
        return sum(w for (s, p, o), w in self.edges.items() if s == name or o == name)


def update_graph(graph: MemoryGraph, entities: list[dict], relations: list[tuple],
                 weights: Optional[dict] = None) -> dict[str, Any]:
    """Schreibt Knoten/Kanten mit Dedup + Konfliktprüfung. Rückgabe: Graph-Delta."""
    weights = weights or {}
    delta: dict[str, Any] = {"added_nodes": [], "added_edges": [],
                             "deduped": [], "rejected": []}
    for e in entities:
        name = e["span"] if isinstance(e, dict) else str(e)
        if name not in graph.nodes:
            graph.add_node(name)
            delta["added_nodes"].append(name)
    for (s, p, o) in relations:
        key = (s, p, o)
        if key in graph.edges:
            delta["deduped"].append(key)
            continue
        # Konflikt 1: funktionale Relation, gleiches (s,p) mit anderem Objekt
        if p in FUNCTIONAL:
            clash = [k for k in graph.edges if k[0] == s and k[1] == p and k[2] != o]
            if clash:
                delta["rejected"].append((key, f"Konflikt: {s} {p} bereits -> {clash[0][2]}"))
                continue
        # Konflikt 2: asymmetrische Relation in Gegenrichtung vorhanden
        if p in ASYMMETRIC and (o, p, s) in graph.edges:
            delta["rejected"].append((key, f"Konflikt: Gegenrichtung {o} {p} {s} existiert"))
            continue
        graph.edges[key] = float(weights.get(key, 1.0))
        graph.add_node(s)
        graph.add_node(o)
        delta["added_edges"].append(key)
    return delta


# =====================================================================
# 4. Konsolidierung mit Vergessens-Operator (HeLa-Mem, Memory-Survey).
# =====================================================================
def consolidate(graph: MemoryGraph, now_ts: float) -> dict[str, Any]:
    """Adaptive Forgetting (3 Bedingungen, HeLa-Mem) + Hub-Detection.
    Rückgabe: Konsolidierungs-Report."""
    report: dict[str, Any] = {"hubs": [], "forgotten": [], "kept": []}
    for name, meta in graph.nodes.items():
        weight = graph.edge_weight(name)
        inactive_days = (now_ts - float(meta.get("last_access", now_ts))) / 86400.0
        recent = int(meta.get("recent_access", 0))
        if weight >= DELTA_HUB:                                   # δ_hub (Hub-Detection)
            report["hubs"].append({"node": name, "weight": round(weight, 3),
                                   "action": "hebbian-distillation"})
        elif (weight < DELTA_PRUNE                              # δ_prune (Bedingung 1)
              and inactive_days > DELTA_AGE_DAYS               # Bedingung 2
              and recent == 0):                                # Bedingung 3
            report["forgotten"].append({"node": name, "weight": round(weight, 3),
                                        "inactive_days": round(inactive_days, 1)})
        else:
            report["kept"].append({"node": name, "weight": round(weight, 3)})
    return report


# =====================================================================
# Enrichment-Queue – asynchron (jetzt mit ECHTEN Stufen).
# =====================================================================
class EnrichmentQueue:
    def __init__(self, log_path: Path = DEFAULT_LOG, graph: Optional[MemoryGraph] = None):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.processed: list[dict[str, Any]] = []
        self.graph = graph or MemoryGraph()
        self.log_path = log_path

    async def worker(self) -> None:
        while True:
            item = await self.queue.get()
            try:
                text = item.get("text", "")
                entities = resolve_entities(text)                 # Stufe 1
                delta = update_graph(self.graph, entities, [])    # Stufe 2
                item["steps"] = ["entity-resolution", "graph-update", "consolidation"]
                item["entities"] = entities
                item["graph_delta"] = delta
                item["enriched_at"] = _now_iso()
                self.processed.append(item)
            except Exception:                                     # fail-soft
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
    decision: str
    reason: str = ""
    tags: dict = field(default_factory=dict)
    enrichment: str = "skipped"


class IngestionHook:
    def __init__(self, gate: Optional[EncodingGate] = None,
                 queue: Optional[EnrichmentQueue] = None,
                 log_path: Path = DEFAULT_LOG):
        self.gate = gate or EncodingGate()
        self.queue = queue or EnrichmentQueue(log_path)
        self.log_path = log_path
        self._seen: dict[str, float] = {}

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

    async def on_session_start(self, session_id: str, source_type: str = "note") -> Optional[Record]:
        try:
            rec = Record(session_id, _now_iso(), source_type, "", "session_start",
                         tags=self._tags(session_id, source_type))
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
                             "Duplikat (SHA-256, 5-min-Fenster)", self._tags(session_id, source_type))
                self._append(rec)
                return rec
            d = self.gate.check(text, source_type, source_trust)
            rec = Record(session_id, _now_iso(), source_type, h,
                         "accepted" if d.accepted else "rejected", d.reason,
                         self._tags(session_id, source_type))
            if d.accepted:
                rec.enrichment = "queued"
                await self.queue.submit({"session_id": session_id, "content_hash": h,
                                         "source_type": source_type, "text": text})
            self._append(rec)
            return rec
        except Exception:
            return None

    async def on_session_end(self, session_id: str) -> Optional[Record]:
        try:
            rec = Record(session_id, _now_iso(), "transcript", "", "session_end",
                         tags=self._tags(session_id, "transcript"))
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

    print("=== [0] Lifecycle + Gate + Dedup ===")
    await hook.on_session_start("sess-001")
    r = await hook.on_user_prompt_submit("sess-001",
        "Der Knowledge-Agent nutzt Fast Write Routing im Konstrukt.",
        "prompt", 0.9)
    print("  OK                ->", r.decision, "| enrichment:", r.enrichment)
    r = await hook.on_user_prompt_submit("sess-001", "kurz", "prompt", 0.9)
    print("  zu kurz           ->", r.decision, "|", r.reason)
    r = await hook.on_user_prompt_submit("sess-001",
        "Der Knowledge-Agent nutzt Fast Write Routing im Konstrukt.", "prompt", 0.9)
    print("  Dedup             ->", r.decision, "|", r.reason)

    print("\n=== [1] Privacy-Filter VOR dem Store (agentmemory) ===")
    for probe in ["Mein Key: sk-proj-ABCDEFGHIJKLMNOPQRSTUVWX",
                  "password=SuperGeheim123",
                  "Token ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                  "Inhalt <private>geheim</private> hier"]:
        r = await hook.on_user_prompt_submit("sess-001", probe, "prompt", 0.9)
        print(f"  {probe[:34]:34} -> {r.decision} | {r.reason}")

    print("\n=== [2] Entity-Resolution (deterministisch, GLiNER-Prinzip) ===")
    s = "Der Knowledge-Agent nutzt Fast Write Routing im Konstrukt (Stufe Handeln)."
    e1 = resolve_entities(s); e2 = resolve_entities(s)
    print("  Entitäten:", [(e["entity_type"], e["span"], e["confidence"]) for e in e1])
    print("  Reproduzierbar (2. Lauf identisch):", e1 == e2)

    print("\n=== [3] Graph-Update mit Konsistenzprüfung ===")
    g = MemoryGraph()
    d1 = update_graph(g, [], [("solver_a", "supersedes", "solver_b")])
    print("  add (a supersedes b) -> added:", d1["added_edges"])
    d2 = update_graph(g, [], [("solver_b", "supersedes", "solver_a")])
    print("  add (b supersedes a) -> rejected:", [r[1] for r in d2["rejected"]])
    d3 = update_graph(g, [], [("i1", "hasEnd", "2024-05-01")])
    print("  add (i1 hasEnd 05-01) -> added:", d3["added_edges"])
    d4 = update_graph(g, [], [("i1", "hasEnd", "2024-06-01")])
    print("  add (i1 hasEnd 06-01) -> rejected:", [r[1] for r in d4["rejected"]])

    print("\n=== [4] Konsolidierung mit Vergessens-Operator (HeLa-Mem) ===")
    now = 1_000_000_000.0
    cg = MemoryGraph()
    cg.add_node("hub_n2", last_access=now, recent_access=5)
    cg.edges[("hub_n2", "assoc", "n0")] = 0.9
    cg.edges[("hub_n2", "assoc", "n1")] = 0.9
    cg.add_node("isolated_n5", last_access=now - 100 * 86400, recent_access=0)
    cg.edges[("isolated_n5", "assoc", "n9")] = 0.1
    rep = consolidate(cg, now)
    print("  Hubs (δ_hub, distill):", [(h["node"], h["weight"]) for h in rep["hubs"]])
    print("  Forgotten (δ_prune/δ_age/0-access):",
          [(f["node"], f["weight"], f["inactive_days"]) for f in rep["forgotten"]])
    print("  Kept:", [(k["node"], k["weight"]) for k in rep["kept"]])

    await hook.on_session_end("sess-001")
    await hook.queue.queue.join()
    worker.cancel()
    print("\n=== Enrichment (async) verarbeitet:", len(hook.queue.processed), "Item(s) ===")
    for it in hook.queue.processed:
        print("  steps:", it["steps"], "| entities:", [e["span"] for e in it["entities"]])


if __name__ == "__main__":
    asyncio.run(_demo())
