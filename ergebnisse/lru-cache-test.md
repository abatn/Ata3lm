# LRU-Cache-Test – Tier 3 Working Memory (max. 15)

> Datum: 2026-10-01
> Zweck: Tier 3 als LRU-bounded Cache testen (20 Router-Durchläufe).
> Quellen: FluxMem (LRU, arXiv:2602.14038), Pichay (Pinning, arXiv:2603.09023),
> TraceRetain (bounded retention, arXiv:2606.29178).
> Lab-Prinzip: keine Erfindung – LRU/Bounded/Pinning aus den Quellen; 15 = Auftrag.

---

## 1. LRU-Logik (nach jedem Router-Durchlauf)

| Entscheidung | Kriterium | Quelle |
|---|---|---|
| **Bleibt in Tier 3** | hohe Abrufhäufigkeit × Kritikalität (pinned) | Pichay (pinning) |
| **Nach Tier 2 auslagern** | LRU-Eviction bei Überschreitung | FluxMem (LRU) |
| **Verwerfen** | (nicht im Test; Tier 2 behält alles) | — |

**Wörtlich (FluxMem):** „When this limit is exceeded, older pages are irreversibly
transferred … using a recency-based **Least Recently Used (LRU) policy**."

---

## 2. Test: 20 Router-Durchläufe

**Datei:** `data/memory/tier3-working/lru_cache.py`

- Capacity: **15** (Auftrag).
- Pinned: `identity`, `ontology` (Tier-1-Kern, nie verdrängt).
- 20 Durchläufe: je ein neues Item + gelegentlicher Zugriff (`item-{i-2}` bei i%3==0).

**Ergebnis (real):**
```json
{
  "capacity": 15,
  "final_size": 15,
  "pinned": ["identity", "ontology"],
  "evicted_count": 7,
  "evicted": ["item-2","item-3","item-1","item-5","item-6","item-4","item-8"]
}
```

### Verlauf

| Phase | Durchläufe | Tier-3-Größe | Ereignis |
|---|---|---|---|
| Füllen | 1–13 | 2 → 15 | Items werden geladen (kein Overflow) |
| Bounded | 14–20 | 15 (konstant) | je 1 LRU-Eviction → 7 ausgelagert |

- **Final:** 15 aktive Items (bounded) ✅
- **Pinned:** `identity`, `ontology` blieben (nie verdrängt) ✅
- **Ausgelagert:** 7 Items nach Tier 2 (`data/memory/tier2-index/evicted-index.md`) ✅

### LRU-Korrektheit
`item-2` wurde zuerst verdrängt (ältestes, nie zugegriffen), dann `item-3`, `item-1`
(zuletzt bei Durchlauf 3 zugegriffen → später verdrängt). Reihenfolge = LRU. ✅

---

## 3. Ergebnis-Dateien

| Datei | Inhalt |
|---|---|
| `data/memory/tier3-working/lru_cache.py` | LRU-Cache-Implementierung |
| `data/memory/tier2-index/evicted-index.md` | ausgelagerte Items (Tier 2) |
| `data/memory/tier3-working/README.md` | Dokumentation |

---

## 4. Quellen (HTTP 200, verifiziert 2026-10-01)

- FluxMem (bounded capacity + LRU): https://arxiv.org/abs/2602.14038
- Pichay (demand paging + Pinning): https://arxiv.org/abs/2603.09023
- TraceRetain (bounded retention): https://arxiv.org/abs/2606.29178
- Eviction-Vergleich (LRU/FIFO/LFU): https://arxiv.org/abs/2608.20280

---

## 5. Status

| Punkt | Status |
|---|---|
| LRU-bounded Cache (max 15) | ✅ `lru_cache.py` |
| 20 Router-Durchläufe simuliert | ✅ (Füllen 2→15, dann 7 Evictions) |
| Pinning | ✅ (identity, ontology) |
| Auslagerung nach Tier 2 | ✅ (evicted-index.md) |
| search-before-store | ✅ (kein Duplikat) |

**Ehrlich:** LRU + Bounded + Pinning stammen aus den Quellen (FluxMem/Pichay/TraceRetain);
die Zahl **15** ist die Projekt-Vorgabe (Auftrag), nicht aus den Quellen (FluxMem nutzt z. B. 4).
