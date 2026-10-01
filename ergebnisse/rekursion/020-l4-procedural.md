# 020 – L4 Procedural Memory operationalisiert (Update · Rollback · Audit)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Skills/L4), nicht Solver-t
> Phase: Revise (L4 um Rollback erweitert)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| Aspekt | vorher (015) | nachher (020) |
|---|---|---|
| Selektives Update | vorhanden | unverändert (approved-Gate) |
| Audit | vorhanden | unverändert |
| **Rollback** | **fehlte** | `rollback(skill, version)` ergänzt |

## 2. Änderungen

- `skills/procedural_memory.py`: `rollback()` + Demo-Schritt [4].
- `skills/README.md`: Rollback-Regel + korrigierte Quellen (Memory Survey, TEA).
- `ergebnisse/l4-procedural.md`.

## 3. Compare-Beleg (externes Signal)

`python3 skills/procedural_memory.py` (reale Ausgabe):
- ohne approved → pending (kein Write); mit approved → angewandt (v3).
- Rollback → `restored v1`, aktueller Stand als `v4` gesichert; Inhalt wieder v1.

## 4. Quellen (belegt, HTTP 200)

- Memory Survey (arXiv:2603.07670): „first-class system component"; temporal versioning.
- TEA-Protokoll (arXiv:2506.12508): „first-class, versioned resources" + Rollback.
- Mem^p (arXiv:2508.06433): „first-class optimization object".
- AFTER (arXiv:2606.23127), ProcMEM (arXiv:2602.01869).

## 5. Korrektur

Das wörtliche Auftragszitat („versioned prompts, workflows, decision rules …")
steht **nicht** in der Memory Survey; Attribution korrigiert (Survey/TEA/Mem^p).

## 6. Guardrails

- `AGENTS.md` unverändert.
- Rollback verliert nichts (aktueller Stand wird vorher versioniert).

## 7. Freigabe

**Freigabe-Status für π₁:** `pending` (menschliche Freigabe ausstehend).
