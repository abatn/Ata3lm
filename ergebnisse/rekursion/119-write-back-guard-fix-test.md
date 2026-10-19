# Rekursion 119 — Testergebnis: Write-Back-Guard-Fix

## Lauf

Befehl (Python 3.11-venv, `/tmp/kvenv`):

```
pytest tests/test_heldout_split.py tests/test_grader_consistency.py tests/test_slow_consolidation.py -v -k "not lifecycle_runner_hook"
```

**Ergebnis:** `43 passed, 1 deselected`. Exit-Code 1, aber nur wegen der Coverage-Schwelle
(`fail-under=100`, Gesamtcoverage 21 % bei diesem Teil-Lauf). Kein Test ist rot.

## Nicht abgeschlossen

- `tests/test_slow_consolidation.py::test_lifecycle_runner_hook` wurde **nicht** zu Ende
  geführt. Der Test hing über mehr als 15 Minuten bei `lifecycle_runner.run_cycle(...)`
  (echte API-Aufrufe, siehe `tests/conftest.py`). Der Lauf wurde beendet.
  Dieser Test ist daher **nicht verifiziert**, weder grün noch rot.
  *(Nachtrag nach dem Fix: `test_lifecycle_runner_hook` verifiziert — `1 passed`, siehe „Endstand".)*
- Der volle `make test` mit 100 % Coverage wurde in diesem Schritt nicht ausgeführt.

## Relevante Tests (alle grün)

- `test_heldout_split.py`: 8 Tests (u. a. `test_base_rate_guard_abstains_on_zero_base`)
- `test_grader_consistency.py`: 4 Tests (u. a. `test_run_guard_base_rate_flags_zero_base_hits`)
- `test_slow_consolidation.py`: alle Write-Back-Tests grün, darunter
  `test_write_back_guard_einwand_abstain_kein_flush` (Guard direkt über den
  `guard_fn`-Parameter, unverändert) und `test_write_back_guard_kein_einwand_flusht`.

Der Guard-Pfad in `slow_consolidation.write_back` ist unverändert, nur der Aufruf aus
`write_back_cycle.main` ist entfernt. Die Tests prüfen den Parameter direkt und bleiben gültig.

## Diff (`kaggle/write_back_cycle.py`, 5 Zeilen ergänzt, 1 entfernt)

```diff
@@ -340,6 +340,11 @@ def _run_guard(probe_results: list):
     Ohne Ergebnisse ⇒ Einwand ("keine Items").
+
+    NICHT am Write-Back verdrahtet (Rek. 118): arXiv:2608.22215 §3.4 kennt nur die
+    Per-Fakt-Regel ``mean(EM) ≥ τ_flush`` ohne Base-Rate-Bedingung; neu eingeführte
+    Fakten (Base = 0) würden sonst nie geflusht. Die Funktion bleibt für andere
+    Pfade erhalten.
@@ -638,7 +643,6 @@ def main(argv=None) -> int:
         state_path=state_path,
-        guard_fn=_run_guard,
     )
```

## Score / Drift

Keine Modellparameter- oder Prompt-Änderung → n/a.

## Offen

- ~~`test_lifecycle_runner_hook` vollständig klären~~ → **behoben** (siehe unten).
- Vollständiger `make test` mit 100 % Coverage.
- ~~Nicht committet, nicht gepusht~~ → **committet & gepusht** (`4bd63cb`).

## Lifecycle-Test: Ursache + Fix

**Ursache (belegt):** `test_lifecycle_runner_hook` (`test_slow_consolidation.py:516`)
ruft `lr.run_cycle(...)` ohne `reflect_fn` → Default `reflective_agent.parse_transition_delta`
(`lifecycle_runner.py:457`) → echter OpenAI-Client bei gesetztem `OPENAI_API_KEY`
(`reflective_agent.py:~115-133`). Retry: `llm_retry.py:22-24` (10× bis 30 s).
Stiller Hänger: `except Exception: return None` verschluckt Fehler.

**Fix (belegt):** `monkeypatch.delenv("OPENAI_API_KEY", raising=False)` ergänzt —
exakt dasselbe Muster wie `test_lifecycle_runner.py:22`
(`# Denken offline -> NOOP (kein Fake)`). Kein Fake, nur Isolation.

**Diff:**
```diff
 def test_lifecycle_runner_hook(tmp_path, monkeypatch):
     import lifecycle_runner as lr
+    monkeypatch.delenv("OPENAI_API_KEY", raising=False)  # Denken offline -> NOOP (kein Fake)
     monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "drift-reference.json"))
```

## Endstand (nach Fix)

**Nach Fix: 44 passed** (`test_lifecycle_runner_hook`: `1 passed in 1.67s`) —
Teil-Lauf oben (43 passed, 1 deselected) + der zuvor hängende Hook-Test.
Vollständiger `make test` mit 100 % Coverage bleibt offen.

## Freigabe (§9.3)

| Approver | Status | Datum |
|---|---|---|
| Batnini | `first_approved` | 2026-10-16 |
| Taoufik | `second_approved` → `approved` | 2026-10-16 |
