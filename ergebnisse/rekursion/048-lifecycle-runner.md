# Rekursion 048: 8-Stufen-Runner (lifecycle_runner.py)

> Datum: 2026-10-04 · Tiefe: `t=47 → t=48` · Phase: **Konstrukt → Akt**
> Freigabe: Batnini (Auftrag). Interface-Änderung → §9 approved.
> Ziel `g`: Schicht-1-Lücke („8 Stufen nur Doku") mit echtem Runner schließen (AGENTS.md §3).

## 1. Quellen (verifiziert, §6)

- AGENTS.md §3 (8-Stufen-Zyklus) — Gesetz.
- `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` (Lese-/Schreib-Semantik + Phasen-Mapping).

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/lifecycle_runner.py` | **neu**: `run_cycle` (8 Stufen), `STAGE_MECHANISM` |
| `tests/test_lifecycle_runner.py` | **neu**: 4 Tests (echter Durchlauf) |
| `ergebnisse/runner-8-stufen.md` | **neu** (Doku + echte Ausgabe) |
| `ergebnisse/reverse-engineering-vollstaendig.md` | Schicht 1 von „nur Doku" → „teilweise (Runner)" |

## 3. Compare-Beleg (extern, echt)

```text
8 Stufen ausgeführt; Stufe 3 ruft pipeline.route_and_store (mandate=ALLOW, fwr=write-new,
trust=PII entfernt, write=write-new); Stufe 6 E_dV=-0.1 damping=1.0; Stufe 8 DI=0.0 gate=ok
pytest test_lifecycle_runner.py: 4 passed · lifecycle_runner.py 100 % Line+Branch
```

**Score** = 4/4 Tests = 100 %. **Drift:** additiv (1 Modul, 1 Test, 2 Docs).

## 4. Gate (§9)

- Interface-Änderung → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: Stufenfolge + Stufe→Modul = **Auftrag** (AGENTS.md §3 erlaubt das:
  „gesetzte Ordnung, kein Paper-Claim"). Stufe 5 ruft die **echte** LLM-Reflexion
  (`parse_transition_delta`); offline → NOOP, keine erfundene Matrix (Guardrail 7).
