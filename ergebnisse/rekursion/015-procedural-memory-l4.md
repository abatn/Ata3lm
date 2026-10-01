# 015 – Procedural Memory als First-Class-Architekturelement (L4)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Skills/Prozeduren), nicht Solver-t
> Phase: Konstrukt (neues Architekturelement) + Revise (Skill-Verwaltung)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| | vorher | nachher |
|---|---|---|
| Skills | 14 lose `SKILL.md` | 14 aktive + `versions/v1/`-Snapshots |
| Änderung | kein Audit, kein Gate | `AUDIT.md` + Diff + **nur mit `approved`** |
| Rolle | Prompt-Text | **First-Class L4** (Procedural Memory) |

## 2. Änderungen

- `+ skills/README.md` — L4-Doku (Versionierung, Audit, selektives Update).
- `+ skills/procedural_memory.py` — Mechanismus (snapshot/audit/propose_update).
- `+ skills/AUDIT.md` + `skills/audit-diffs/` — Audit-Trail.
- `+ skills/<name>/versions/v1/SKILL.md` — 14 Baseline-Snapshots.
- `+ ergebnisse/procedural-memory.md`.

## 3. Compare-Beleg (externes Signal)

Selbsttest `python3 skills/procedural_memory.py` (reale Ausgabe):
- 14 v1-Snapshots erstellt.
- **ohne** `approved` → `applied=False` (Inhalt unverändert).
- **mit** `approved` → `applied=True`, Version angelegt.

## 4. Quellen (belegt, HTTP 200)

- https://arxiv.org/abs/2508.06433 (Mem^p – procedural memory as first-class)
- https://aclanthology.org/2026.findings-acl.866.pdf (Mem^p, ACL Findings 2026)
- https://arxiv.org/abs/2606.23127 (AFTER – Skill als first-class artifact)
- https://arxiv.org/abs/2602.01869 (ProcMEM – PPO-Gate vor Skill-Aufnahme)
- https://arxiv.org/abs/2510.04851 (LEGOMem)
- https://arxiv.org/abs/2512.13564 (Memory in the Age of AI Agents)
- https://arxiv.org/abs/2602.06052 (Survey)
- https://arxiv.org/abs/2602.05665 (Graph-based Agent Memory)

## 5. Schwellen/Konventionen (Auftrag)

`versions/vN/` als Snapshot-Ort; `versions/` reserviert; Audit in `AUDIT.md`;
Update nur bei `approved`. (Kein Paper schreibt diese konkrete Mechanik vor.)

## 6. Guardrails

- Kein Skill ohne `approved` geändert (Human-Gate `AGENTS.md` §9).
- `AGENTS.md` **unverändert**.
- Idempotente Snapshots (kein Audit-Duplikat bei gleichem Inhalt).

## 7. Freigabe

**Freigabe-Status für π₁:** `approved: Batnini, 2026-10-01`.
