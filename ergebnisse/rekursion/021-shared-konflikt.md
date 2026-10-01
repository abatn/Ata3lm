# 021 – Shared Memory: Konfliktauflösung konkretisiert (Trigger · Trust · Validierung)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Shared Memory), nicht Solver-t
> Phase: Revise (SharedTier erweitert)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| Aspekt | vorher (018) | nachher (021) |
|---|---|---|
| Trigger | gleicher Key, versch. Werte | unverändert (explizit) |
| Auflösung | prefer newest + Supersede | + **Trust-Score** (niedrigerer Trust verliert) |
| Kollisionsvalidierung | – | **vor jedem Write** (ACL/leer/Schema) |

## 2. Änderungen

- `data/memory/shared/shared_memory.py`: `trust`-Scores, `validate_write()`,
  trust-basierte Auflösung (`phase: resolution`), `Entry.trust`.
- `data/memory/shared/README.md`: Trust + Kollisionsvalidierung.
- `ergebnisse/shared-konflikt.md`.

## 3. Compare-Beleg (externes Signal)

`python3 data/memory/shared/shared_memory.py` (reale Ausgabe):
- Trigger: agentA (0.9) v1; agentB (0.5) → **rejected** (niedrigerer Trust).
- agentA (0.9) → v2, supersedes v1.
- Kollisionsvalidierung: Schema-Verstoß + leerer Wert → **rejected** (phase validation).

## 4. Quellen (belegt, HTTP 200)

- Memory Survey (arXiv:2603.07670) §6.5 (consistency under concurrent writes),
  §9.6 (governance „wide open"), Write-Path (source attribution).
- Collaborative Memory (arXiv:2505.18279); Graphiti (arXiv:2501.13956).

## 5. Abgrenzung (Auftrag)

Trust-Grenze, Schema, Supersede-Marker = **Auftrag** (Survey: „wide open").
Datei real: `data/memory/shared/shared_memory.py` (Auftrag nannte anderen Pfad).

## 6. Guardrails

- `AGENTS.md` unverändert; kein Löschen (Supersede); Trust senkt Schreibrechte nicht unter ACL.

## 7. Freigabe

**Freigabe-Status für π₁:** `approved: Batnini, 2026-10-01`.
