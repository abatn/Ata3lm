# Tier 3 – Working Memory (bounded LRU-Cache)

> Schicht: Tier 3 (Working Memory) der 3-Schicht-Gedächtnis-Pipeline.
> Zweck: begrenzter Cache für aktuell geladene Wissensseiten (max. 15 aktive Items).
> Quelle (hierarchisches Memory + Working Context + Pinning + Eviction): MemGPT
> (arXiv:2310.08560) – "working context is a fixed-size read/write block";
> "System instructions are read-only and **pinned** to main context";
> "queue eviction policy".
> Quelle (semantisches Caching + Eviction + Prefetching): Cortex (arXiv:2509.17360).
> Lab-Prinzip: keine Erfindungen – nur Auftrag + Quellen.

## Regel (Auftrag, quellenbasiert)

- **Bounded:** max. **15 aktive Items** (Auftrag).
- **LRU:** bei Überschreitung wird das am längsten unbenutzte Item verdrängt.
- **Pinning:** bestimmte Items sind angepinnt und werden **nicht** verdrängt.

Quelle: MemGPT (Working Context als "fixed-size block" + "pinned" System-Instruktionen
+ Eviction-Policy), Cortex (Eviction-Policy).

## Aufbau

| Feld | Bedeutung |
|---|---|
| `id` | eindeutige Item-ID |
| `concept` | Konzept aus Tier 2 |
| `ort` | geladene Datei (Tier 1/2) |
| `last_used` | Zeitstempel der letzten Nutzung (LRU) |
| `pinned` | true = nicht verdrängbar |

## Ablauf

```text
Anfrage ──▶ Tier 2 (Concept Index) ──▶ passende Orte ──▶ Tier 3 (Working Memory)
                                                              │
                                       max 15 Items, LRU-Eviction (außer pinned)
```

## Aktueller Zustand

- **Items aktiv:** 15 (bounded; nach 20 Router-Durchläufen).
- **Max:** 15 (Auftrag).
- **Pinned:** `identity`, `ontology` (Tier-1-Kern; nie verdrängt).
- **Ausgelagert:** 7 Items (nach Tier 2, `data/memory/tier2-index/evicted-index.md`).

## Operative Implementierung (LRU-Cache)

**Datei:** `data/memory/tier3-working/lru_cache.py`

```text
Router-Durchlauf ─▶ search-before-store (kein Duplikat)
                 ─▶ store / access
                 ─▶ bei > 15: LRU-Eviction (ältestes nicht-gepinntes Item)
                 ─▶ ausgelagert nach Tier 2 (Konzept-Index)
```

**LRU-Regel (Quelle: FluxMem, arXiv:2602.14038):** „When this limit is exceeded,
older pages are irreversibly transferred … using a recency-based **Least Recently
Used (LRU) policy**."
**Pinning (Quelle: Pichay, arXiv:2603.09023):** „pin working-set pages identified
by fault history".
**Bounded retention (Quelle: TraceRetain, arXiv:2606.29178):** „evicts the
lowest-scoring entries at capacity".

## Befüllungslogik (Ingestion → Tier 3)

**Datei:** `data/memory/tier3-working/lru_cache.py` (`fill_from_structured`)

```text
Ingestion-Zyklus (knowledge/structured/ → Router)
        │
        ▼
Relevanz = Abrufhäufigkeit × Kritikalität   (TraceRetain, arXiv:2606.29178)
        │
        ▼
Relevante Items laden (rel >= 0.5)
  - entity-* / distilled-*  -> rel 1.0 -> geladen + GEPINNT
  - relation-*              -> rel 0.6 -> geladen (nicht gepinnt)
        │
        ▼
Tier 3 (max 15) ── LRU-Eviction ──▶ Tier 2 (Konzept-Index)
```

**search-before-store:** `store` prüft `key in items` → kein Duplikat.

**Test (20 Durchläufe):**
- Befüllt aus `knowledge/structured/` (5 Entitäten + 2 Relationen)
- Pinned (7): identity, ontology + 5 Entitäten/Destillate
- Bounded bei 15; 14 ausgelagert (Relationen + alte Items)

Details: `ergebnisse/lru-befuellung.md`.

## Quellen

- MemGPT (hierarchisches Memory, Working Context, Pinning, Eviction): https://arxiv.org/abs/2310.08560
- Cortex (semantisches Caching, Eviction, Prefetching): https://arxiv.org/abs/2509.17360
- **FluxMem** (bounded capacity + LRU): https://arxiv.org/abs/2602.14038
- **Pichay** (demand paging + Pinning): https://arxiv.org/abs/2603.09023
- **TraceRetain** (bounded retention): https://arxiv.org/abs/2606.29178
- Eviction-Vergleich (LRU/FIFO/LFU): https://arxiv.org/abs/2608.20280

Test (20 Durchläufe): `ergebnisse/lru-cache-test.md`.
