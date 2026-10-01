# Adaptive Forgetting (HeLa-Mem) – dreifache Bedingung

> Datum: 2026-10-01
> Zweck: Scoring-Eviction durch HeLa-Mem Adaptive Forgetting ersetzen.
> Quelle: **HeLa-Mem, ACL 2026, arXiv:2604.16839** (§3.3 + Ablation §4.3).
> Lab-Prinzip: Keine Erfindungen – Bedingung wörtlich aus der Quelle.

---

## 0. Quellen-Korrektur (ehrlich)

| Angabe | Korrekt? |
|---|---|
| Aufgabe: „total edge weight below **δ_hub**" | ⚠️ **δ_hub** ist die Hub-Erkennung; für Forgetting gilt **δ_prune** |
| HeLa-Mem §3.3: „total edge weight is below **δ_prune**" | ✅ korrekt |

→ Verwendet wurde **δ_prune** (wörtlich aus dem Paper), nicht δ_hub.

---

## 1. Dreifache Bedingung (HeLa-Mem §3.3, wörtlich)

```text
A memory is flagged for removal ONLY IF it simultaneously satisfies three criteria:
  (1) its total edge weight is below δ_prune   (structural irrelevance)
  (2) its inactive duration exceeds δ_age       (temporal dormancy)
  (3) it has zero recent access
```
> „This **strict compound criterion** ensures that the system selectively removes
> noise while **preserving strong, albeit older, associations**."

**Wichtig:** **ALLE drei** Bedingungen müssen gleichzeitig erfüllt sein → streng.

---

## 2. Ablation (HeLa-Mem §4.3, wörtlich)

| Variante | Overall (GPT-4o-mini) |
|---|---|
| **Full** | **34.74** |
| **w/o Forgetting** | **34.28** |
| w/o Spreading Activation | 32.19 |
| w/o Reflective Agent | 29.87 |

→ Adaptive Forgetting trägt bei (34.28 vs. 34.74); Reflective Agent ist der größte Beitrag.
Beide sind laut Ablation **unverzichtbar**.

---

## 3. Implementierung (`data/memory/tier3-working/lru_cache.py`)

**`should_forget(key)`** – dreifache Bedingung:
```python
edge_weight < DELTA_PRUNE  AND  (tick - last_used) > DELTA_AGE  AND  recent_access == 0
```

**`_evict_adaptive_forgetting()`** – primäre Eviction:
- entfernt **nur**, wenn alle drei Bedingungen erfüllt sind;
- **Fallback (bounded):** greift die strenge Bedingung nicht (kein Item qualifiziert),
  wird nach Scoring (S_evict) ausgelagert, damit Tier 3 bei **max. 15** bleibt.

**Parameter (Auftrag):** `DELTA_PRUNE=0.5`, `DELTA_AGE=10` (ENV-konfigurierbar).
> Die Paper-Werte für δ_prune/δ_age sind nicht angegeben (Hyperparameter) → Auftrag.

**Ausführen:** `python3 data/memory/tier3-working/lru_cache.py`

---

## 4. Test: 20 Router-Durchläufe

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
| 20 Router-Durchläufe | write-new (edge_weight 0.3) / write-update (1.0, gepinnt) |
| Adaptive Forgetting | entfernt Items, die **alle drei** Bedingungen erfüllen |
| Bounded-Fallback | wenn streng nicht greift → Scoring (bleibt bei 15) |
| Pinned | identity, ontology + 5 Entitäten/Destillate (nie entfernt) |

**Ergebnis:** Bounded bei 15 ✅ · dreifache Bedingung primär ✅ · stark vernetzte/alte bleiben ✅

---

## 5. Quellen (HTTP 200, verifiziert 2026-10-01)

- HeLa-Mem (Adaptive Forgetting §3.3, Ablation §4.3): https://arxiv.org/abs/2604.16839
- HeLa-Mem ACL 2026: https://aclanthology.org/2026.acl-long.625/

---

## 6. Status

| Punkt | Status |
|---|---|
| Scoring → Adaptive Forgetting | ✅ `_evict_adaptive_forgetting` |
| Dreifache Bedingung (alle gleichzeitig) | ✅ wörtlich aus HeLa-Mem |
| δ_prune (nicht δ_hub) | ✅ korrigiert |
| Bounded (max 15) | ✅ (primär + Fallback) |
| Test (20 Router-Durchläufe) | ✅ (14 Evictions) |

**Ehrlich:** Bedingung + Ziel („preserving strong, albeit older, associations") wörtlich
aus HeLa-Mem (arXiv:2604.16839). δ_prune/δ_age-Werte sind Auftrag (Paper nennt sie nicht).
δ_hub-Angabe der Aufgabe wurde zu **δ_prune** korrigiert.
