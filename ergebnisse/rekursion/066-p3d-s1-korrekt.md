# Rekursion 066: P3d/S1-korrekt — Drift-Referenz §-konform

> Datum: 2026-10-05 · Tiefe: `t=65 → t=66` · Phase: **Revise**
> Freigabe: `approved` (Batnini, „go mit Bedingung 1–3", Lesart A).
> Ziel `g`: Drift-Stufe 8 (§9.1c/§9.2b) §-konform reparieren — **nicht** wie der
> zurückgesetzte S1 (`reference = observed` ⇒ immer `ok`).

## 1. Quellen (verifiziert, §6)
- `AGENTS.md` §5 (`M(t)→M(t+1)`), §9:116/122, §9.1c (Z.163–174, kalibriert),
  §9.2b (Z.195–200, Ground-Truth-Checkpoint), §10.4 (Z.281–282, unsicher → ask).
- Quelle Drift-Bound: arXiv:2603.06333 (Goal Drift Index, gelernte Thresholds).

## 2. Änderung (Diff)
| Datei | Änderung |
|---|---|
| `data/memory/lifecycle_runner.py` | Referenz-Priorität (explizit → Env → Checkpoint → keine); Cold-Start ⇒ `ask` + Bootstrap; Checkpoint-Fortschreibung nur bei `ok`; Helfer `_load/_save_drift_reference`, `_configured_drift_baseline` |
| `tests/test_lifecycle_runner.py` | Bedingung 3 (injizierte Baseline im alten Test) + 7 neue Tests (§9.1d) |
| `tests/conftest.py` | Bedingung 1: `LIFECYCLE_DRIFT_REFERENCE` global auf tmp |
| `.gitignore` | `data/memory/tier2-index/drift-reference.json` |

## 3. Compare-Beleg (extern, echt)
```text
Cold-Start (keine Referenz)  -> DI=None gate=ask (+ Bootstrap)   §10.4
Checkpoint == Beobachtung    -> DI=0.0  gate=ok                  §9.2b
verschobene Verteilung       -> DI=1.0  gate=ask                 §9.2b
Fortschreiben nur bei ok     -> deny => Referenz unverändert     §9
kein Repo-Write              -> verifiziert (conftest/​.gitignore)
Volle Suite: 368 passed · 100 % (2793/678)
```
**Anti-Muster geprüft:** Referenz ≠ self ✓ · Cold-Start ⇒ ask ✓ · alter Test nicht
abgeschwächt ✓ · kein „self"-Default ✓.

## 4. Gate (§9) + Provenienz
- Verhaltensänderung → `approved` (Mensch); G4 unberührt; G6 (kein Git) eingehalten.
- §9.1b: `AGENTS.md`/`tier1-base` unverändert ⇒ kein `versions/vN`.
- Peer-Doku: `ergebnisse/p3d-s1-fix.md`.
