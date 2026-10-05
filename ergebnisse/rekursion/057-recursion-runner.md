# Rekursion 057: 5-Phasen-Runner (recursion_runner.py)

> Datum: 2026-10-04 · Tiefe: `t=56 → t=57` · Phase: **Konstrukt → Akt**
> Freigabe: Batnini (Auftrag) — **approved**. Interface-Änderung → §9 approved.
> Ziel `g`: Konstrukt→Akt→Observe→Compare→Revise als echten Runner ausführen.

## 1. Quellen (verifiziert, §6)

- SEAA (arXiv:2609.17331): HMM mit editierbarer Zustandsübergangsmatrix; Reflexion aktualisiert die HMM-Parameter.
- AGENTS.md §2 (5 Phasen).

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/recursion_runner.py` | **neu**: `run_recursion`, `_phase_konstrukt/akt/observe/compare/revise` |
| `tests/test_recursion_runner.py` | **neu**: 3 Tests (Zyklus, NOOP, Akt-Deny) |
| `ergebnisse/runner-5-phasen.md` | **neu** (Doku + echte Ausgabe) |

## 3. Compare-Beleg (extern, echt)

```text
run_recursion(...): Konstrukt K=4 · Akt write-new · Observe [] · Compare belief=0.3426 · Revise skipped=false
pytest test_recursion_runner.py: 3 passed · recursion_runner.py 100 % Line+Branch
Volle Suite: 324 passed · 100 % (2640/616)
```

**Score** = 3/3 Tests = 100 %. **Drift:** additiv (1 Modul, 1 Test, 1 Doku).

## 4. Gate (§9)

- Interface-Änderung → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: Phasenfolge = Auftrag; Compare nutzt `best_belief` (nicht den vollen Grader-Loop).
