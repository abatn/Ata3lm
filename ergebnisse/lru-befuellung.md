# LRU-Befüllung – Tier 3 Working Memory (Ingestion → Tier 3)

> Datum: 2026-10-01
> Zweck: Befüllungslogik für Tier 3 (aus knowledge/structured/ → Router).
> Quellen: FluxMem (LRU, arXiv:2602.14038), TraceRetain (Relevanz, arXiv:2606.29178),
> Pichay (Pinning, arXiv:2603.09023).
> Lab-Prinzip: keine Erfindung – LRU/Relevanz/Pinning aus den Quellen; 15 = Auftrag.

---

## 1. Befüllungslogik

```text
1. Ingestion-Zyklus: knowledge/structured/ → Router
2. Relevanz = Abrufhäufigkeit × Kritikalität (TraceRetain)
3. Relevante Items laden (rel >= 0.5); search-before-store (kein Duplikat)
4. LRU-Logik:
     - bleibt in Tier 3?  (pinned / hohe Relevanz)
     - nach Tier 2?       (LRU-Eviction bei Überschreitung)
     - verworfen?         (nicht im Test; Tier 2 behält alles)
5. Bounded: max. 15 aktive Items
```

**Relevanz-Stufen (Auftrag, nach TraceRetain-Feature-Idee):**
| Typ | Relevanz | Aktion |
|---|---|---|
| `entity-*` / `distilled-*` | 1.0 | laden + **pinnen** |
| `relation*` | 0.6 | laden (nicht gepinnt) |
| Sonstige | 0.3 | nicht laden |

**Wörtlich (TraceRetain):** „scores entries by interpretable features (success, age,
access frequency, redundancy, specificity, similarity, downstream utility) and evicts
the lowest-scoring ones at capacity."

---

## 2. Test: 20 Router-Durchläufe

**Datei:** `data/memory/tier3-working/lru_cache.py` (`simulate_20_router_runs`).

**Ergebnis (real):**
```json
{
  "capacity": 15,
  "final_size": 15,
  "pinned": ["identity","ontology","distilled-hub-n2","entity-fast-write-routing",
             "entity-solver-berechne-durchschnitt","entity-solver-berechne-median",
             "entity-solver-finde-minimum"],
  "evicted_count": 14,
  "evicted": ["relation-agent-uses-fwr","relations-rekursion-solver",
              "item-2","item-3","item-1","item-5","item-6","item-4","item-8",
              "item-9","item-7","item-11","item-12","item-10"]
}
```

### Verlauf

| Phase | Ergebnis |
|---|---|
| Initialbefüllung | 5 Entitäten/Destillate geladen + gepinnt; 2 Relationen geladen |
| 20 Durchläufe | Tier 3 füllt bis 15, dann LRU-Eviction |
| Eviction-Reihenfolge | zuerst Relationen (rel 0.6, nicht gepinnt), dann alte Items |
| Pinned | identity, ontology + 5 Entitäten/Destillate (nie verdrängt) |

**Ergebnis:** Bounded bei 15 ✅ · Pinning funktioniert ✅ · 14 ausgelagert nach Tier 2 ✅

---

## 3. Ergebnis-Dateien

| Datei | Inhalt |
|---|---|
| `data/memory/tier3-working/lru_cache.py` | Befüllungs- + LRU-Logik |
| `data/memory/tier2-index/evicted-index.md` | ausgelagerte Items (Tier 2) |
| `data/memory/tier3-working/README.md` | Dokumentation |

---

## 4. Quellen (HTTP 200, verifiziert 2026-10-01)

- FluxMem (bounded capacity + LRU): https://arxiv.org/abs/2602.14038
- TraceRetain (Relevanz-Scoring + Eviction): https://arxiv.org/abs/2606.29178
- Pichay (demand paging + Pinning): https://arxiv.org/abs/2603.09023
- Eviction-Vergleich (LRU/FIFO/LFU): https://arxiv.org/abs/2608.20280

---

## 5. Status

| Punkt | Status |
|---|---|
| Initialbefüllung (Ingestion → Tier 3) | ✅ `fill_from_structured` |
| Relevanz (Abrufhäufigkeit × Kritikalität) | ✅ (TraceRetain-Idee) |
| LRU-Logik (bleibt / Tier 2 / verworfen) | ✅ |
| Bounded (max 15) | ✅ |
| 20 Router-Durchläufe | ✅ (gefüllt + 14 Evictions) |
| search-before-store | ✅ (kein Duplikat) |

**Ehrlich:** LRU + Relevanz + Pinning stammen aus den Quellen (FluxMem/TraceRetain/Pichay);
die Zahl **15** und die konkreten Relevanz-Stufen (1.0/0.6/0.3) sind die Projekt-Bindung
(Auftrag) – klar markiert.
