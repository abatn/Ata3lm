# Rekursion 047: HeLa-Mem Spreading Activation (Dual-Path)

> Datum: 2026-10-04 · Tiefe: `t=46 → t=47` · Phase: **Compare → Revise**
> Freigabe: Batnini („ok go"). Interface-Änderung → §9 approved.
> Ziel `g`: LRU/PPR um HeLa-Mems lokale **Spreading Activation** (1 Hop) ergänzen.

## 1. Quellen (verifiziert, §6)

- **HeLa-Mem** arXiv:2604.16839 (ACL 2026.625), §3.3/§3.4 — wörtlich:
  - Adaptive Forgetting: drei Bedingungen gleichzeitig (edge_weight < δ_prune,
    age > δ_age, zero recent access).
  - Hub Detection: „associative strength exceeds a threshold δ_hub".
  - Spreading: „S(v_j) = S_base(v_j) + β·Σ_{i∈N(j)} S_base(v_i)·w_ij".
  - Dual-Path: Base-top-k ∪ Spread-top-m.

**Korrektur der Aufgabe:** LRU war **nicht** Default (Default `policy="value"` =
Adaptive Forgetting); CAPACITY=15 (nicht >15); Adaptive Forgetting + Hub waren bereits da.

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/tier3-working/lru_cache.py` | **neu**: `spread_activation_scores`, `dual_path_retrieval`, `fill_from_spreading`, `HELA_BETA/TOP_K/TOP_M` |
| `tests/test_lru_cache.py` | **+5 Tests** (Hub/Isoliert, 1-Hop, Dual-Path, Fill) |
| `ergebnisse/adaptive-forgetting.md` | **neu** (Diff + Test) |
| `connectors/hela-semantic.md` | Implementierungs-Referenz ergänzt |

## 3. Compare-Beleg (extern, echt)

```text
Adaptive Forgetting: evakuiert = isoliert | hub bleibt = True
Spreading 1 Hop: base[b]=0.000 -> spread[b]=0.500
                 2 Hops c: base == spread (unberührt)
Dual-Path: [('a','base'), ('b','base'), ('d','spread')]
```

**Score** = 5/5 neue Tests = 100 %. **Drift:** additiv (Funktionen + Tests + Doku).

## 4. Gate (§9)

- Interface-Änderung → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: β=0.5, k=5, m=3 = **Auftrag** (Paper nennt keine Zahlen);
  PPR (GAAMA) bleibt zusätzlich erhalten.
