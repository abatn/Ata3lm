# Wertbewusste Eviction (HTM-EAR)

> Datum: 2026-10-01
> Zweck: reine LRU-Eviction in `lru_cache.py` durch wertbewusstes Scoring ersetzen.
> Quelle: **HTM-EAR, arXiv:2603.10032** (2026) – „Importance-Preserving Tiered
> Memory with Hybrid Routing under Saturation".
> Lab-Prinzip: Keine Erfindungen – Formel + Werte wörtlich aus der Quelle.

---

## 1. Formel (HTM-EAR, wörtlich)

```text
S_evict = α · importance + β · min( usage/10 , 1 )        mit α = 0.75, β = 0.25
```
- „Items with the **lowest scores** are evicted (approximately **15 % of capacity**).
  Evicted items are inserted into L2."
- **Retrieval-Score (ebenfalls HTM-EAR):** `S_retrieve = sim³ + λ·overlap + γ·importance`.

**Die Platzhalter der Aufgabe sind damit belegt:**
| Platzhalter | Offizieller Wert (HTM-EAR) |
|---|---|
| α (Gewicht importance) | **0.75** |
| β (Gewicht usage) | **0.25** |
| usage-Normalisierung | **10** |
| Eviction-Menge | ~15 % der Kapazität |

**Ablation (HTM-EAR, wörtlich):**
- „LRU minimizes latency (21.1 ms) but loses essential information (**2416 essential facts evicted**)."
- Full system: **MRR = 1.000**; Oracle: 0.997 ± 0.003.
- BGL-Logs: Full system **MRR 0.336**, Oracle 0.370, **LRU 0.069**.

---

## 2. Implementierung (`data/memory/tier3-working/lru_cache.py`)

**Ersetzt:** `_evict_lru` (rein nach Alter) → `_evict_lowest_score` (nach S_evict).

```python
def evict_score(self, key):
    # HTM-EAR: S_evict = α·importance + β·min(usage/10, 1)
    return 0.75 * self.items[key]["importance"] + 0.25 * min(hits/10, 1)
```

- Jedes Item trägt `importance` (0–1) + `hits` (usage) → kontinuierlich aktualisiert.
- Eviction: niedrigster `S_evict` (außer `pinned`).
- `policy="lru"` bleibt als Vergleichsbaseline erhalten.

---

## 3. Test: 20 Router-Durchläufe (LRU vs. wertbewusst)

**Ausführen:** `EVICT_COMPARE=1 python3 data/memory/tier3-working/lru_cache.py`

| | Evicted |
|---|---|
| **LRU** | relation-agent-uses-fwr, relations-rekursion-solver, item-2, item-3, item-1, item-4, item-6, item-7, item-5, item-8, item-10, item-11, item-9, item-12 |
| **Wertbewusst** | relation-*, item-2, item-3, item-4, item-6, item-7, item-8, item-10, item-11, item-12, **item-14, item-15, item-16** |

**Unterschied (durch Scoring):**
- **Value behält** statt Eviction: **item-1, item-5, item-9** (diese hatten `write-update` → importance 1.0).
- **Value evictet zusätzlich:** item-14, item-15, item-16 (write-new, importance 0.8, ungenutzt).

→ Statt „ältestes zuerst" entscheidet **S_evict** (importance × usage). Wichtige
(hoch-importance) Items bleiben, ungenutzte werden zuerst ausgelagert. ✅

---

## 4. Quellen (HTTP 200, verifiziert 2026-10-01)

- HTM-EAR (Importance-Preserving Tiered Memory): https://arxiv.org/abs/2603.10032
- HTM-EAR Code: https://github.com/shubham-61291/HTM-EAR

---

## 5. Status

| Punkt | Status |
|---|---|
| LRU → wertbewusstes Scoring | ✅ `_evict_lowest_score` |
| Formel S_evict (α=0.75, β=0.25, usage/10) | ✅ wörtlich aus HTM-EAR |
| kontinuierlicher Utility-Wert (importance + usage) | ✅ |
| Test (20 Durchläufe, LRU vs. Value) | ✅ (Evictions unterscheiden sich) |
| LRU-Baseline erhalten | ✅ (`policy="lru"`) |

**Ehrlich:** Formel + Werte (α=0.75, β=0.25, usage/10, ~15 %) wörtlich aus HTM-EAR
(arXiv:2603.10032). Die konkreten importance-Werte (0.8/1.0) sind die Projekt-Bindung
(Auftrag, an die Router-Klassen gebunden) – klar markiert.
