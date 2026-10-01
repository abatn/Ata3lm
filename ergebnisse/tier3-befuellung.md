# Tier3-Befüllung – nach fast_write_router-Durchlauf

> Datum: 2026-10-01
> Zweck: Initialbefüllung von Tier 3 nach jedem Router-Durchlauf.
> Quellen: ZenBrain (arXiv:2604.23878), Memory Survey (arXiv:2603.07670),
>          HTM-EAR (arXiv:2603.10032, Eviction-Scoring).
> Lab-Prinzip: Keine Erfindungen – Kriterium + Mechanismus aus den Quellen.

---

## 0. Quellen-Korrektur (ehrlich)

| Angabe | Korrekt? |
|---|---|
| Aufgabe: „ZenBrain (arXiv:19413933)" | ❌ **ungültig** (404 „Article identifier not recognized") |
| **ZenBrain** = arXiv:**2604.23878** (Bering 2026) | ✅ korrekt |
| Memory Survey = arXiv:2603.07670 | ✅ korrekt („Memory for Autonomous LLM Agents") |

→ Verwendet wurde die **korrekte** ZenBrain-Quelle: **arXiv:2604.23878**.

---

## 1. Kriterium (Quellen)

**Wörtlich (ZenBrain, arXiv:2604.23878):** „Working Memory maintains the active task
focus with **limited capacity** (∼7 items). It provides the **highest-priority retrieval
and fastest access**, evicting items to short-term memory on task completion."

**Memory Survey (arXiv:2603.07670):** „Memory for Autonomous LLM Agents: Mechanisms,
Evaluation, and Emerging Frontiers" → Budget-basierte Verwaltung.

**Kriterium (Auftrag):** **erwartete Zugriffshäufigkeit × Kritikalität**.
- `write-update` (bestehend, kritisch): Kritikalität 1.0
- `write-new` (neu): Kritikalität 0.8
- `non-write`: **nicht** laden (nur Rekursions-Historie)

---

## 2. Implementierung (`data/memory/tier3-working/lru_cache.py`)

**`fill_from_router(router_output)`:**
```text
nach jedem fast_write_router-Durchlauf:
  non-write      -> überspringen (nur Historie)
  write-new      -> laden (Kritikalität 0.8)
  write-update   -> laden + PINNEN (Kritikalität 1.0)
  Relevanz = erwartete Zugriffshäufigkeit × Kritikalität >= 0.8
  bei > 15: Eviction nach S_evict (HTM-EAR, niedrigster Score) -> Tier 2
```

**Bounded + Auslagerung (nicht mehr rein LRU):** Statt „ältestes zuerst" entscheidet
**S_evict = 0.75·importance + 0.25·min(usage/10, 1)** (HTM-EAR, arXiv:2603.10032).
Niedrigster Score wird ausgelagert.

**Ausführen:** `python3 data/memory/tier3-working/lru_cache.py`

---

## 3. Test: 20 Router-Durchläufe

**Simulation:** 20 Durchläufe, je `write-new` + (alle 4) `write-update` + (alle 5) `non-write`.

**Ergebnis (real):**
```json
{
  "policy": "value",
  "capacity": 15,
  "final_size": 15,
  "pinned": ["identity","ontology","distilled-hub-n2","entity-fast-write-routing",
             "entity-solver-berechne-durchschnitt","entity-solver-berechne-median",
             "entity-solver-finde-minimum"],
  "evicted_count": 14,
  "evicted": ["relation-agent-uses-fwr","relations-rekursion-solver",
              "item-2","item-3","item-4","item-6","item-7","item-8",
              "item-10","item-11","item-12","item-14","item-15","item-16"]
}
```

### Verlauf
| Phase | Ergebnis |
|---|---|
| Initialbefüllung | 5 Entitäten/Destillate (gepinnt) + 2 Relationen |
| 20 Router-Durchläufe | write-new/write-update geladen; **non-write übersprungen** |
| Bounded | bei 15 konstant; 14 Evictions (nach S_evict) → Tier 2 |
| Pinned | identity, ontology + 5 Entitäten/Destillate (nie verdrängt) |

**Ergebnis:** Bounded bei 15 ✅ · non-write übersprungen ✅ · Scoring-Eviction ✅

---

## 4. Quellen (HTTP 200, verifiziert 2026-10-01)

- ZenBrain (7-Layer Memory, Working Memory = aktiver Cache): https://arxiv.org/abs/2604.23878
- ZenBrain Code: https://github.com/zensation-ai/zenbrain
- Memory Survey: https://arxiv.org/abs/2603.07670
- HTM-EAR (Eviction-Scoring): https://arxiv.org/abs/2603.10032

---

## 5. Status

| Punkt | Status |
|---|---|
| Befüllung nach Router-Durchlauf | ✅ `fill_from_router` |
| Kriterium (Zugriffshäufigkeit × Kritikalität) | ✅ |
| Bounded (max 15) | ✅ |
| Auslagerung nach Scoring (S_evict) | ✅ (HTM-EAR) |
| 20 Router-Durchläufe | ✅ (gefüllt + 14 Evictions) |
| non-write → nur Historie | ✅ |

**Ehrlich:** Working-Memory-Mechanismus (aktiver Cache, höchste Priorität, Eviction)
aus ZenBrain (arXiv:2604.23878); Budget-Sicht aus Memory Survey (arXiv:2603.07670);
Eviction-Scoring aus HTM-EAR (arXiv:2603.10032). Falsche Quellenangabe (19413933)
**korrigiert**. Zahl 15 + Kritikalitäts-Werte = Auftrag.
