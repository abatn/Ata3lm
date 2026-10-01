# 026 – Shared Memory: Trust-basierte Supersession (Write-Time)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Shared Memory), nicht Solver-t
> Phase: Revise (Status-Modell + superseded_by)
> Auslöser: menschlicher Auftrag vom 2026-10-01. Baut auf 018/021 auf.

## 1. Zustand vorher / nachher

| Aspekt | vorher (021) | nachher (026) |
|---|---|---|
| Status | valid/superseded | **confirmed / superseded / contested** (LatticeMind) |
| Unterlegener Eintrag | rejected (nicht gespeichert) | **behalten** + `superseded_by` (supersede-not-erase) |

## 2. Änderungen

- `data/memory/shared/shared_memory.py`: `Entry.superseded_by`, Status-Modell,
  write-time Trust-Auflösung (superseded_old / superseded_new / contested).
- `ergebnisse/shared-supersession.md`.

## 3. Compare-Beleg (externes Signal)

`python3 data/memory/shared/shared_memory.py` (reale Ausgabe):
- agentA(0.5) v1 confirmed; agentB(0.9) → v1 **superseded_by v2** (B gewinnt);
  agentC(0.3) → v3 superseded_by v2 (behalten, nicht gelöscht).
- Kollisionsvalidierung: Schema/leer → phase validation.

## 4. Quellen (belegt, HTTP 200)

- LatticeMind (arXiv:2608.08236): write-time conflict resolution, Status, Checker, Supersession.
- Governed Collaborative Memory (arXiv:2605.04264): supersede-not-erase, version lineage.
- Memory Survey (arXiv:2603.07670): consistency under concurrent writes; source attribution.

## 5. Abgrenzung (Auftrag)

Trust-Score als Entscheider (Proxy für LatticeMinds „evidence-weighted") + konkrete
Grenze = **Auftrag**; Mechanik = **Belegt**.

## 6. Guardrails

- `AGENTS.md` unverändert; kein Löschen (supersede-not-erase); distinkte Werte je Version.

## 7. Freigabe

**Freigabe-Status für π₁:** `pending` (menschliche Freigabe ausstehend).
