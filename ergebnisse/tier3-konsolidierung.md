# Tier-3-Konsolidierung (Aufgabe 5)

> Datum: 2026-10-01
> Status: **Belegt** (Mechanik) + **Auftrag** (Kapazität 15)
> Befund: Aufgabe 5 war **bereits implementiert** in
> `data/memory/tier3-working/lru_cache.py`. Dieses Dokument hält den Ist-Stand fest.

## 1. Auftrag

- `tier3-working/` nach jedem Router-Lauf befüllen.
- Max. 15 Items, Scoring-Eviction.

## 2. Ist-Stand (verifiziert am Code)

| Anforderung | Umsetzung | Datei:Zeile |
|---|---|---|
| Nach Router-Lauf befüllen | `fill_from_router(router_output)` | `lru_cache.py:156` |
| Aus Ingestion befüllen | `fill_from_structured(min_relevance)` | `lru_cache.py:136` |
| Kapazität 15 | `CAPACITY = 15` | `lru_cache.py:29` |
| Scoring-Eviction | `_evict_lowest_score()` / `evict_score()` | `lru_cache.py:125,208` |
| Adaptives Vergessen | `_evict_adaptive_forgetting()` / `should_forget()` | `lru_cache.py:113,193` |
| Pinning (Working Set) | `store(..., pinned=True)` | `lru_cache.py:87` |
| Auslagerung nach Tier 2 | `self.evicted` → `tier2-index/evicted-index` | `lru_cache.py:66` |

## 3. Belegte Mechanik (Quellen)

- **Bounded Capacity + LRU:** FluxMem — arXiv:2602.14038
  („recency-based Least Recently Used (LRU) policy").
- **Demand Paging + Pinning:** Pichay — arXiv:2603.09023
  („pin working-set pages identified by fault history"; Pin-Stärke zerfällt).
- **Lowest-Score-Eviction bei Kapazität:** TraceRetain — arXiv:2606.29178
  („evicts the lowest-scoring entries at capacity").
- **Eviction-Vergleich:** arXiv:2608.20280 („Use LFU as the simple baseline").
- **Adaptive Forgetting (3 Bedingungen):** HeLa-Mem — arXiv:2604.16839 §3.3
  (alle drei müssen gleichzeitig erfüllt sein):
  1. `total edge weight < delta_prune` (strukturelle Irrelevanz)
  2. `inactive duration > delta_age` (temporale Dormanz)
  3. `zero recent access`
- **Wertbewusstes Eviction-Scoring:** HTM-EAR — arXiv:2603.10032
  `S_evict = α·importance + β·min(usage/10, 1)`, α=0.75, β=0.25.
- **Hierarchisches Memory (3-Tier):** ARIADNE — arXiv:2105.09864;
  Dual-Layer — arXiv:2608.22215.

## 4. Status der Zahl „15"

**Auftrag (Projekt-Vorgabe)**, nicht forschungsbelegt. FluxMem nutzt z. B. 4
(STIM). Die Quellen belegen das *Prinzip* „bounded capacity", nicht den Wert 15.

## 5. Ergebnis

- Anforderung „max. 15 Items, Scoring-Eviction" ist **erfüllt**.
- Anforderung „nach jedem Router-Lauf befüllen" ist über `fill_from_router`
  **erfüllt**.
- Keine Code-Änderung nötig; dieses Dokument ist die geforderte Doku.

## 6. Quellen (keine Erfindungen)

- https://arxiv.org/abs/2602.14038 (FluxMem)
- https://arxiv.org/abs/2603.09023 (Pichay)
- https://arxiv.org/abs/2606.29178 (TraceRetain)
- https://arxiv.org/abs/2608.20280 (Eviction-Vergleich)
- https://arxiv.org/abs/2604.16839 (HeLa-Mem, Adaptive Forgetting)
- https://arxiv.org/abs/2603.10032 (HTM-EAR)
- https://arxiv.org/abs/2105.09864 (ARIADNE, 3-Tier)
- https://arxiv.org/abs/2608.22215 (Dual-Layer Agentic Memory)
