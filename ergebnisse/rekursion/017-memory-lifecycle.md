# 017 – Memory-Lifecycle (Konsolidierung, Forgetting, Konfliktlösung)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Memory), nicht Solver-t
> Phase: Revise (Lifecycle-Operatoren)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| Operator | vorher | nachher |
|---|---|---|
| Konsolidierung | Hub-Distillation (vorhanden) | dokumentiert (ontology.md §D) |
| Forgetting | **nur 1 Bedingung** (weight) | **3 Bedingungen** (weight ∧ age ∧ access) |
| Konfliktlösung | fehlte | `resolve_conflict` (Supersede-Marker) |

## 2. Änderungen

- `data/memory/reflective_agent.py`: `detect_forgetting` → 3 Bedingungen;
  neu `resolve_conflict` + `simulate_lifecycle`; `__main__`-Branch `MEMORY_LIFECYCLE_SIM=1`.
- `data/memory/tier1-base/ontology.md` §D (Memory-Lifecycle).
- `data/memory/tier1-base/versions/v2/` (Snapshot vor Änderung).
- `ergebnisse/memory-lifecycle.md`.

## 3. Compare-Beleg (externes Signal)

`MEMORY_LIFECYCLE_SIM=1 python3 data/memory/reflective_agent.py` (reale Ausgabe):
- Konsolidierung: `hub_n2` → hebbian-distillation.
- Forgetting: `isolated_n5` (weight 0.01, age 100, access 0) → vergessen.
- Konflikt: `current_version` `durchschnitt`→`median`; alter Fakt superseded.

## 4. Quellen (belegt)

- HeLa-Mem (arXiv:2604.16839; ACL 2026): Hub-Distillation + Adaptive Forgetting (3 Bed.).
- Memory Survey (arXiv:2603.07670): contradiction detection + temporal versioning (prefer newest).
- Graphiti (arXiv:2501.13956): bi-temporal, invalidieren statt löschen.

**Ehrliche Zuordnung:** Konfliktlösung = Memory Survey (+ Graphiti), **nicht** HeLa-Mem.

## 5. Schwellen (Auftrag)

δ_prune=0.05, δ_age=60 Tage (τ=60 belegt aus HeLa-Mem).

## 6. Guardrails

- `AGENTS.md` unverändert; tier1-base versioniert (v2-Snapshot).
- Forgetting konservativ: fehlende Metadaten = „aktiv" (kein Löschen).

## 7. Freigabe

**Freigabe-Status für π₁:** `approved: Batnini, 2026-10-01`.
