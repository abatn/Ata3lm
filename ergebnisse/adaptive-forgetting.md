# Adaptive Forgetting + HeLa-Mem Spreading Activation (Dual-Path)

> Datum: 2026-10-04 · Status: **Belegt** (Quelle) + **Auftrag** (β, Capacity, 1-Hop).
> Quelle **verifiziert**: HeLa-Mem — arXiv:2604.16839 (18 Apr 2026), **ACL 2026** —
> https://aclanthology.org/2026.acl-long.625/ · Code https://github.com/ReinerBRO/HeLa-Mem
> Guardrail 7: alle Zahlen real ausgeführt (`data/memory/tier3-working/lru_cache.py`).

## 1. Quelle (wörtlich, §3.3/§3.4)

- **Adaptive Forgetting:** „A memory is flagged for removal only if it simultaneously
  satisfies three criteria: (1) its total edge weight is below δ_prune …, (2) its
  inactive duration exceeds δ_age …, and (3) it has zero recent access."
- **Hub Detection:** „a node v_i is flagged for consolidation if its associative
  strength exceeds a threshold δ_hub".
- **Spreading Activation:** „S(v_j) = S_base(v_j) + β · Σ_{i∈N(j)} S_base(v_i) · w_ij".
- **Dual-Path:** „the base path selects the top-k nodes by S_base, and the flip path
  promotes up to m additional nodes … by spreading-augmented score S".

## 2. Ist-Stand / Diff (ehrlich, §6)

| Element | Status |
|---|---|
| Dreifache Bedingung (`should_forget`, `lru_cache.py`) | **schon vorhanden** |
| `_evict_adaptive_forgetting` (Default `policy="value"`) | **schon vorhanden** |
| Hub-Detection (GAAMA `hub_dampening_threshold=50`) | **schon vorhanden** |
| Dual-Path via **GAAMA-PPR** | schon vorhanden |
| **HeLa-Mem Spreading Activation** (1 Hop, β) | **NEU** |
| `WorkingMemory.fill_from_spreading` (tier2→tier3) | **NEU** |

**Korrektur der Ausgangslage:** `lru_cache` nutzt **nicht** LRU als Default — Default
ist `policy="value"` = Adaptive Forgetting **primär**; LRU ist nur die Vergleichs-Baseline
(`policy="lru"`). `CAPACITY = 15` (nicht „> 15").

## 3. Implementierung (neu, additiv)

```text
S_base(v) = cosine(q, e_v)                      # Base-Pfad
S(v_j)    = S_base(v_j) + β·Σ_{i∈N(j)} S_base(v_i)·w_ij   # EINE Stufe, lokal
Retrieval = Base-top-k  ∪  Spread-top-m         # Dual-Path
```
- `spread_activation_scores()` / `dual_path_retrieval()` / `WorkingMemory.fill_from_spreading()`
- **β = 0.5 = Auftrag** (Paper nennt β ohne Wert); k=5, m=3 = Auftrag.
- Unterschied zu PPR: **lokal/eine Stufe** (nur direkte Nachbarn) statt globalem
  Random-Walk über den ganzen Graphen. PPR bleibt erhalten (GAAMA-Quelle).

## 4. Test (echt, Guardrail 7)

```text
Adaptive Forgetting: evakuiert = isoliert | hub bleibt = True
Spreading 1 Hop: base[b]=0.000 -> spread[b]=0.500 (verstärkt)
                 2 Hops c: base=0.000 == spread=0.000 (unberührt)
Dual-Path: [('a','base'), ('b','base'), ('d','spread')]
```

| Test (`tests/test_lru_cache.py`) | Prüft |
|---|---|
| `test_hub_bleibt_isolierter_knoten_evakuiert` | **Hub bleibt, isolierter Knoten wird evakuiert** |
| `test_spread_activation_eine_stufe` | direkter Nachbar verstärkt, 2 Hops nicht |
| `test_dual_path_retrieval_base_und_spread` | Base-top-k ∪ Spread-top-m |
| `test_fill_from_spreading` | tier2→tier3 Ladepfad |

## 5. Gate (§9)

- Interface-Änderung (neue Funktionen/Methode) → **approved** (Batnini, „ok go").
- Guardrail 3: Provenienz `ergebnisse/rekursion/047-spreading-activation.md`.
- Guardrail 6: kein Commit ohne Erlaubnis. §9.1b: `AGENTS.md` unverändert.
- **Ehrliche Grenzen:** β/k/m = Auftrag (Paper nennt keine Zahlen); Adaptive Forgetting
  + Hub waren bereits implementiert (kein „Ersatz" von LRU nötig).

## 6. Quellen

- HeLa-Mem (ACL 2026): https://aclanthology.org/2026.acl-long.625/ · arXiv:2604.16839
- HeLa-Mem Code: https://github.com/ReinerBRO/HeLa-Mem
