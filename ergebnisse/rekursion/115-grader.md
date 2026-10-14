# Rekursion 115: P-A einheitlicher Grader + Base-Rate-Guard

- **Datum:** 2026-10-14 · **Phase:** Konstrukt/Akt-Folgewirkung · kein Compare-Lauf in dieser Iteration (kein Kaggle-/GPU-Lauf).
- **Freigabe:** Auftrag 2026-10-14 (§9/§9.3). Record: `ergebnisse/freigabe-record-115-2026-10-14.json`. Die frühere Freigabe an `cacfe66e07607698` gilt **nicht mehr** (Stand vor dem Testfall „führende Leerzeile“). Für den aktuellen SHA `8f205d99b66ffe7b` liegt **keine** Zwei-Personen-Freigabe vor: `state = pending`.
- **Diff-SHA (§9.1d):** aktuell `8f205d99b66ffe7b` = sha256 über `git diff HEAD` der 5 Code-Dateien (`acceptance_gate.py`, `slow_consolidation.py`, `e2e_theta_probe.py`, `write_back_cycle.py`, `tests/test_slow_consolidation.py`) + Inhalt `tests/test_grader_consistency.py`. Nicht gebunden: diese Rek.-Datei selbst. Zur Freigabe: `approve("Batnini", diff_sha=…)` + `approve("Taoufik", diff_sha=…)` ⇒ `approved`. Bis dahin `pending`.
- **Trennung:** Kaskaden-Teil (P-C) ist in **Rek. 116** (eigene Iteration).
- **Ehrlichkeitshinweis:** Die Personen sind im Record nur als Text vermerkt. Sie sind nicht kryptografisch authentifiziert (Caveat Rek. 108).

## 1. Ziel g

Probe, Flush und Gate entscheiden mit derselben Metrik (strict EM, §10.5), und der Base-Rate-Guard wirkt im Flush.

## 2. Baseline

- Probe war Teilstring (`gold.lower() in answer.lower()`).
- Rek. 113: strict 6/200 vs. 0/200; substring 9/200 vs. 8/200.

## 3. Diff (line-level, §3)

- `data/memory/acceptance_gate.py` (stdlib-only): `extract_answer`, `grade(answer, gold, mode="strict")`, `base_rate_guard(base_hits, n, min_base_hits=1)`.
- `kaggle/write_back_cycle.py`: `_ThetaProbe.__call__` nutzt `_grade` (= `acceptance_gate.grade`), Z. 77 Import, Z. 341–346 `_run_guard` → `base_rate_guard`, Z. 639 `guard_fn=_run_guard` an `write_back`.
- `data/memory/slow_consolidation.py`: optionaler `guard_fn=None` (Z. 426); Z. 501–502 wertet den Guard nach der Probe-Schleife aus, vor jeder Verbuchung; ohne `guard_fn` unverändert.
- `kaggle/e2e_theta_probe.py`: Z. 29 Import `grade` + `base_rate_guard`; Z. 146 `base_rate_guard` im Ergebnis-JSON.
- **Interface:** nur additiv (optionaler Parameter, Default `None`). Verhaltensänderung: Probe strict; Flush „abstain" bei Basistreffer 0.

## 4. Test

- `tests/test_grader_consistency.py`: 8 Grader-Fälle (inkl. führende Leerzeile, zuvor nicht abgedeckter Branch `acceptance_gate.py:105→104`), Probe/Flush/Gate-Identität, Guard-Abstain.
- `tests/test_slow_consolidation.py`: Guard-Pfade im Flush (neu, 44 Zeilen).
- Gesamtsuite: siehe Abschnitt 6 (Ergebnis wird dort und in der Abschlussmeldung belegt).

## 5. Score-Änderung / Drift

- **Score:** nicht gemessen (kein Kaggle-/GPU-Lauf). Keine Zahl wird behauptet.
- **Drift:** nicht gemessen. Rein additive Interface-Änderung ⇒ Drift `n/a` (Rek. 112 §4).

## 6. Verifikation (Ist-Stand)

- `make test` (`.venv`, Python 3.12, `requirements-dev.txt` gepinnt): erster Lauf **845 passed**; Coverage 99,98 % (1 Zweig fehlte, `acceptance_gate.py:105→104`). Der Fehlzweig ist durch den Testfall „führende Leerzeile" abgedeckt. Der Gesamtlauf wurde danach erneut gestartet; sein Ergebnis steht in der Abschlussmeldung.

## 7. Offen (ehrlich)

- Rek.-109-Zahlen (Teilstring) sind mit strict **nicht** reproduziert. Kaggle-Lauf nötig, bevor eine Θ′-Wirkung behauptet wird.

## 8. Nicht behauptet (§7)

- Keine Wirkungsaussage zu Θ′.
