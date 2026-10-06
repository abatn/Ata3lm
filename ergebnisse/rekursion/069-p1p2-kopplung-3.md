# Rekursion 069: P1/P2-Kopplungsfixes (3. Prüfung) — R04/R05/R06/R07/R10/R16/R17/R18/R19

> Datum: 2026-10-06 · Tiefe: `t=68 → t=69` · Phasen: Observe → Compare → Revise.
> Ziel `g`: Runner-Richtungswechsel (5↔8) crasht nicht, kein Lost-Update, kein stiller
> State-Fehler, kein Lernen aus negativem Compare, kein falsches Drift-`ask`, SHACL
> meldet ohne ausgeführte Inferenz nicht „belastbar".
> Status: **Auftrag** (Betriebsregel). Belegte Mechaniken (CAS/§9-Gate) sind unten je
> Befund zitiert; die Verdrahtung ist Projekt-Auftrag.
> Freigabe der §9-pflichtigen Interfaces: **`approved`** (Batnini, 2026-10-06).

## 1. Quellen / Gesetz (verifiziert)

- `AGENTS.md` §3 (8 Stufen), §9 (Automatisches Gate: Score < 70 % blockiert), §9.1c
  (Drift), §9.2b (Ground-Truth-Checkpoint), §9.3/G4 (Interface-Änderung), Guardrail 6
  (kein Git), Guardrail 7 (echte Tests).
- Bestehende Implementierung: `data/memory/runner_state.py`,
  `lifecycle_runner.py`, `recursion_runner.py`, `shacl_inferenz.py` (Datei:Zeile im Diff).
- `ergebnisse/kopplung-komponenten-bericht.md` (K1/K6-Kontext).

## 2. Änderung (Diff, §9-pflichtige Interfaces markiert)

| Datei | Änderung | Befund |
|---|---|---|
| `data/memory/runner_state.py` | `snapshot(rev=…)` + `save(..., expected_rev=…)` (echtes **CAS**, §9-pflichtige Signatur-Erweiterung); `_current_rev()`; `rev` monoton; Doc-Kommentar „CAS-Ersatz" entfernt | R06 |
| `runner_state.py` | `_wm_state` speichert `policy`; `reconstruct` setzt sie fort; `json.dumps` **ohne** `sort_keys` ⇒ LRU-Reihenfolge (z→a) bleibt | R19 |
| `lifecycle_runner.py` | Resume überschreibt nur, wenn recon-Teil **nicht None** | R05 |
| `lifecycle_runner.py` | Default-Drift (`LIFECYCLE_DRIFT_BASELINE`) + expliziter Monitor gaten **vor** der Mutation; `_CanonicalDriftMonitor`/`_drift_label` = **ein** Labelraum vor/nach | R04, R16 |
| `lifecycle_runner.py` / `recursion_runner.py` | `state_save` im Ergebnis (Fehler nicht verschwiegen); `expected_rev` beim Save; deny ⇒ **kein** State-Write | R07, R18 |
| `recursion_runner.py` | `REVISE_MIN_SCORE=0.70`; Revise nur bei Score ≥ 70 % | R10 |
| `shacl_inferenz.py` | Regeln vorhanden + keine Runde (`max_rounds=0`) ⇒ `conforms_reliable=False` | R17 |
| `tests/test_runner_state.py`, `test_lifecycle_runner.py`, `test_recursion_runner.py`, `test_shacl_inferenz.py` | echte Regressionstests je Befund | — |

Kein Git (`git add/commit/push` nicht ausgeführt, G6). Keine `AGENTS.md`/tier1-base-Änderung.

## 3. Compare (externes Signal, Pflicht)

```text
Pflicht-Set (Auftrag):
.venv/bin/python -m pytest tests/test_runner_state.py tests/test_lifecycle_runner.py \
  tests/test_recursion_runner.py tests/test_shacl_inferenz.py -q --no-cov
-> 59 passed

Coverage (line+branch) der vier geänderten Module:
runner_state 100 % · lifecycle_runner 100 % · recursion_runner 100 % · shacl_inferenz 100 %

Volle Suite (ohne Live-/Endpunkt-gebundene Dateien, die VOR dieser Änderung langsam sind):
412 passed, 2 deselected
Nicht Teil des schnellen Laufs (echte Endpunkt-/HF-Zugriffe, unberührt von diesem Diff):
test_evaluator_version.py · test_fwr.py · test_gaama_extract.py · test_reflective.py ·
test_models_live.py (Marker `network`)

Lint: ruff check (E/F/W/I) auf alle 8 geänderten Dateien -> All checks passed
```

- Je Befund: Fix umgesetzt **und** Test vorhanden (R04–R19, siehe Test-Commits).
- Keine Attrappen (G7): Runner laufen gegen echte Module; offline ⇒ NOOP.

## 4. Gate (§9) + Provenienz

- **§9-pflichtige Interface-Änderungen**: `save(expected_rev=…)`, `snapshot(rev=…)`,
  neue Ergebnis-Felder `state_save`, `_CanonicalDriftMonitor`, `REVISE_MIN_SCORE`
  (Funktionssignatur/Verhalten) — **Freigabe `approved`** (Batnini, 2026-10-06); ein
  `self_update` an `AGENTS.md`/tier1-base ist **nicht** berührt.
- Guardrails: G4 markiert · G6 eingehalten · G7 echte Tests.
- Rollback: einzeilig (Git-Revision dieser 4 Module + Tests).
- Nächstes Self-Feedback: Live-Suite (test_fwr/reflective/gaama/evaluator) mit echtem
  Endpoint nachziehen, sobald verfügbar.
