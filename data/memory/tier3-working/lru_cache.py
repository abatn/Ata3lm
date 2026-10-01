#!/usr/bin/env python3
"""
Tier 3 – Working Memory: LRU-bounded Cache (max. 15 aktive Items).

Quellen (2025–2026, verifiziert):
  - FluxMem (arXiv:2602.14038): bounded capacity + "recency-based Least Recently
    Used (LRU) policy"; bei Überschreitung werden ältere Seiten ausgelagert.
  - Pichay (arXiv:2603.09023): demand paging + "pin working-set pages identified
    by fault history"; pin strength decays.
  - TraceRetain (arXiv:2606.29178): bounded retention, "evicts the lowest-scoring
    entries at capacity".
  - Eviction-Vergleich (arXiv:2608.20280): LRU/FIFO/LFU; "Use LFU as the simple
    baseline".

Lab-Prinzip: keine Erfindung – LRU + Bounded + Pinning + search-before-store
sind aus den Quellen; die Zahl 15 ist die Projekt-Vorgabe (Auftrag).
"""

import json
import os
from collections import OrderedDict
from pathlib import Path

ROOT = Path("/home/opc/knowledge-agent")
TIER3 = ROOT / "data/memory/tier3-working"
TIER2 = ROOT / "data/memory/tier2-index"
STRUCTURED = ROOT / "knowledge/structured"   # Ingestion-Output

CAPACITY = 15  # Projekt-Vorgabe (Auftrag); FluxMem nutzt z. B. 4 (STIM)

# --- HeLa-Mem Adaptive Forgetting (arXiv:2604.16839 §3.3) ---
# Drei Bedingungen (ALLE müssen gleichzeitig erfüllt sein):
#   (1) total edge weight < delta_prune   (strukturelle Irrelevanz)
#   (2) inactive duration > delta_age      (temporale Dormanz)
#   (3) zero recent access
DELTA_PRUNE = float(os.environ.get("HELA_DELTA_PRUNE", "0.5"))
DELTA_AGE = int(os.environ.get("HELA_DELTA_AGE", "10"))


def relevance(path: Path) -> float:
    """Relevanz = Abrufhäufigkeit × Kritikalität (Quelle: TraceRetain, arXiv:2606.29178).

    TraceRetain bewertet Einträge nach interpretierbaren Features (u.a.
    success, access frequency, downstream utility). Hier: Kritikalität nach Typ.
    """
    name = path.name
    if name.startswith("distilled-") or name.startswith("entity-"):
        return 1.0      # hohe Kritikalität (Entitäten / destilliertes Wissen)
    if name.startswith("relation"):
        return 0.6      # mittlere Kritikalität (Beziehungen)
    return 0.3          # niedrig (Sonstiges)


class WorkingMemory:
    """Bounded Cache für aktuell geladene Wissensseiten (Tier 3).

    policy="value" (Default): wertbewusste Eviction (HTM-EAR, arXiv:2603.10032).
    policy="lru": reine LRU-Eviction (Vergleichsbaseline).
    """

    def __init__(self, capacity: int = CAPACITY, policy: str = "value"):
        self.capacity = capacity
        self.policy = policy
        self.items = OrderedDict()   # key -> {value, pinned, last_used, hits}
        self.tick = 0
        self.evicted = []            # nach Tier 2 ausgelagert
        self.log = []

    # --- search-before-store (Quelle: memory-skills) ---
    def search(self, key: str):
        return self.items.get(key)

    # --- LRU-Access: Zugriff verschiebt an das Ende (zuletzt benutzt) ---
    def access(self, key: str):
        self.tick += 1
        if key in self.items:
            self.items[key]["last_used"] = self.tick
            self.items[key]["hits"] += 1
            self.items[key]["recent_access"] = 1   # HeLa-Mem: recent access
            self.items.move_to_end(key)
            self.log.append({"tick": self.tick, "op": "access", "key": key,
                             "size": len(self.items)})
            return self.items[key]
        return None

    # --- Store mit wertbewusster Eviction (HTM-EAR, arXiv:2603.10032) ---
    def store(self, key: str, value: str, pinned: bool = False, importance: float = 0.5,
              edge_weight: float = 1.0):
        self.tick += 1
        if key in self.items:                 # search-before-store: kein Duplikat
            self.access(key)
            return
        self.items[key] = {"value": value, "pinned": pinned,
                           "last_used": self.tick, "hits": 0,
                           "importance": importance,
                           "edge_weight": edge_weight,   # HeLa-Mem: total edge weight
                           "recent_access": 0}           # HeLa-Mem: zero recent access
        self.items.move_to_end(key)
        evicted_key = None
        if len(self.items) > self.capacity:
            if self.policy == "lru":
                evicted_key = self._evict_lru()
            else:
                # Primär: Adaptive Forgetting (dreifache Bedingung, streng)
                evicted_key = self._evict_adaptive_forgetting()
                # Fallback (bounded): greift die strenge Bedingung nicht,
                # wird nach Scoring ausgelagert (bleibt bei max. 15).
                if evicted_key is None:
                    evicted_key = self._evict_lowest_score()
        self.log.append({"tick": self.tick, "op": "store", "key": key,
                         "size": len(self.items), "evicted": evicted_key})

    def should_forget(self, key: str) -> bool:
        """HeLa-Mem Adaptive Forgetting: alle 3 Bedingungen gleichzeitig.

        Wörtlich (arXiv:2604.16839): „A memory is flagged for removal only if it
        simultaneously satisfies three criteria: (1) its total edge weight is below
        δ_prune, (2) its inactive duration exceeds δ_age, and (3) it has zero recent access."
        """
        it = self.items[key]
        return (it.get("edge_weight", 1.0) < DELTA_PRUNE
                and (self.tick - it.get("last_used", self.tick)) > DELTA_AGE
                and it.get("recent_access", 0) == 0)

    def evict_score(self, key: str) -> float:
        """S_evict = α·importance + β·min(usage/10, 1)  (HTM-EAR Eq., α=0.75, β=0.25).

        Quelle: HTM-EAR (arXiv:2603.10032): „S_evict = α·importance +
        β·min(usage/10, 1), with α=0.75, β=0.25. Items with the lowest scores
        are evicted."
        """
        it = self.items[key]
        return 0.75 * it.get("importance", 0.5) + 0.25 * min(it.get("hits", 0) / 10.0, 1.0)


    def fill_from_structured(self, min_relevance: float = 0.5):
        """Initialbefüllung: nach dem Ingestion-Zyklus relevante Items laden.

        Quelle: Memory-Hierarchie — die relevantesten Items aus dem
        Ingestion-Output (knowledge/structured/) werden in Tier 3 geladen.
        search-before-store verhindert Duplikate (store prüft `key in items`).
        """
        loaded = []
        for p in sorted(STRUCTURED.glob("*.md")):
            if p.name == "README.md":
                continue
            rel = relevance(p)
            if rel >= min_relevance:
                before = len(self.items)
                self.store(p.stem, f"aus {p.name}",
                           pinned=(rel >= 1.0))   # hohe Kritikalität -> gepinnt
                if len(self.items) > before or p.stem in self.items:
                    loaded.append(p.stem)
        return loaded

    def fill_from_router(self, router_output: list):
        """Nach jedem fast_write_router-Durchlauf: neue/aktualisierte Einträge laden.

        Kriterium: erwartete Abrufhäufigkeit × Kritikalität.
        Quelle: ZenBrain (arXiv:2604.23878, Working Memory = aktiver Cache,
        höchste Priorität zuerst); Memory Survey (arXiv:2603.07670, Budget-Statistik).
        router_output: Liste von {"class": "write-new"|"write-update", "key": str}.
        """
        loaded = []
        # write-update (bestehend, kritisch) vor write-new
        order = {"write-update": 1.0, "write-new": 0.8}
        for entry in sorted(router_output, key=lambda e: -order.get(e.get("class"), 0.0)):
            cls = entry.get("class")
            if cls not in order:
                continue  # non-write -> nur Historie, nicht Tier 3
            key = entry["key"]
            crit = order[cls]
            # erwartete Abrufhäufigkeit: Zugriffe, falls schon vorhanden, sonst 1
            freq = self.items.get(key, {}).get("hits", 0) + 1
            if freq * crit >= 0.8:
                # edge_weight: write-update stark vernetzt, write-new schwach
                ew = 1.0 if cls == "write-update" else 0.3
                self.store(key, f"router:{cls}", pinned=(cls == "write-update"),
                           importance=crit, edge_weight=ew)
                loaded.append(key)
        return loaded

    def _evict_lru(self):
        """Reine LRU-Eviction (Vergleichsbaseline; HTM-EAR-Ablation)."""
        for key in list(self.items.keys()):
            if not self.items[key]["pinned"]:
                item = self.items.pop(key)
                self.evicted.append(key)
                self._to_tier2(key, item)
                return key
        return None

    def _evict_adaptive_forgetting(self):
        """HeLa-Mem Adaptive Forgetting: entfernt nur bei dreifacher Bedingung.

        Wörtlich: „strict compound criterion … selectively removes noise while
        preserving strong, albeit older, associations." (arXiv:2604.16839)
        """
        for key in list(self.items.keys()):
            if not self.items[key]["pinned"] and self.should_forget(key):
                item = self.items.pop(key)
                self.evicted.append(key)
                self._to_tier2(key, item)
                return key
        # Fallback: kein Item erfüllt die dreifache Bedingung -> nichts entfernen
        return None

    def _evict_lowest_score(self):
        """Wertbewusste Eviction (HTM-EAR): niedrigster S_evict (außer pinned).

        Statt LRU: das Item mit dem niedrigsten S_evict = α·importance +
        β·min(usage/10,1) wird ausgelagert. (HTM-EAR, arXiv:2603.10032)
        """
        candidates = [(k, self.evict_score(k)) for k, v in self.items.items()
                      if not v["pinned"]]
        if not candidates:
            return None  # alles gepinnt
        key = min(candidates, key=lambda kv: kv[1])[0]
        item = self.items.pop(key)
        self.evicted.append(key)
        self._to_tier2(key, item)
        return key

    def _to_tier2(self, key, item):
        """Ausgelagertes Item in den Konzept-Index (Tier 2) schreiben."""
        TIER2.mkdir(parents=True, exist_ok=True)
        path = TIER2 / "evicted-index.md"
        header = "# Tier 2 – Ausgelagerte Items (aus Tier 3)\n\n| Key | Grund | Quelle |\n|---|---|---|\n"
        line = f"| {key} | LRU-Eviction (Tier 3 voll) | FluxMem (arXiv:2602.14038) |\n"
        if path.exists():
            path.write_text(path.read_text() + line)
        else:
            path.write_text(header + line)


def simulate_20_router_runs():
    """20 fast_write_router-Durchläufe: Befüllung → LRU-Auslagerung.

    Jeder Durchlauf liefert write-new / write-update / non-write Einträge;
    Tier 3 lädt die relevanten (erwartete Abrufhäufigkeit × Kritikalität).
    """
    wm = WorkingMemory(capacity=CAPACITY)
    wm.store("identity", "Agent-Identität", pinned=True)
    wm.store("ontology", "8 Stufen / 5 Phasen", pinned=True)
    wm.fill_from_structured()   # Initialbefüllung aus knowledge/structured/
    for i in range(1, 21):
        # simulierter Router-Output pro Durchlauf
        router_out = [{"class": "write-new", "key": f"item-{i}"}]
        if i % 4 == 0:
            router_out.append({"class": "write-update", "key": f"item-{max(1, i-3)}"})
        if i % 5 == 0:
            router_out.append({"class": "non-write", "key": f"skip-{i}"})  # nur Historie
        wm.fill_from_router(router_out)
    return wm


if __name__ == "__main__":
    if os.environ.get("EVICT_COMPARE") == "1":
        import copy as _copy
        def run(policy):
            wm = WorkingMemory(capacity=CAPACITY, policy=policy)
            wm.store("identity", "Agent-Identität", pinned=True, importance=1.0)
            wm.store("ontology", "8 Stufen / 5 Phasen", pinned=True, importance=1.0)
            wm.fill_from_structured()
            for i in range(1, 21):
                out = [{"class": "write-new", "key": f"item-{i}"}]
                if i % 4 == 0:
                    out.append({"class": "write-update", "key": f"item-{max(1,i-3)}"})
                wm.fill_from_router(out)
            return wm
        lru, val = run("lru"), run("value")
        print(json.dumps({
            "lru_evicted": lru.evicted,
            "value_evicted": val.evicted,
            "lru_active": list(lru.items.keys()),
            "value_active": list(val.items.keys()),
        }, ensure_ascii=False, indent=2))
    else:
        wm = simulate_20_router_runs()
        out = {
            "capacity": wm.capacity, "policy": wm.policy,
            "final_size": len(wm.items),
            "active_keys": list(wm.items.keys()),
            "pinned": [k for k, v in wm.items.items() if v["pinned"]],
            "evicted": wm.evicted, "evicted_count": len(wm.evicted),
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
