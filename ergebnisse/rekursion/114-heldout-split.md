# Rekursion 114: P-B — disjunkter Held-out-Split

- **Datum:** 2026-10-14 · **Tiefe:** `t=… → t+1` (System-Iteration, §9.1c Einzelvariable: Split)
- **Phase:** Konstrukt/Akt-Folgewirkung (Trainingsdaten-Auswahl); kein Compare-Lauf in dieser Iteration.

## 1. Anlass

Rek. 109/113 und `knowledge-agent-plan` belegen: Der Trainings-Korpus und das Eval-Set teilen Fragen.
Messung (Auftrag, Quelle HF `write_back_cycle_result.json`): Overlap **20/20 Fragen** und **8/8 `pending_keys`**
mit `ergebnisse/zsre-eval-f6.jsonl` (200 Zeilen, git-getrackt).
Ursache im Code: `kaggle/write_back_cycle.py` lud den Korpus mit `split="validation"`; das Eval-Set kommt aus demselben Split.

## 2. Freigabe (§9 / §9.3)

- `approval.py` `TwoPersonApproval`: `approve("Batnini")` → `first_approved`; `approve("Taoufik")` → `second_approved`; `finalize()` → `approved`.
- Freigabe durch Batnini + Taoufik laut Auftrag (2026-10-14). Namen authentifizieren keine Person (Rek. 108); die Freigabe ist Auftragsbeleg, kein kryptografischer Beleg.
- Der Record ist **nicht** an einen Diff-SHA gebunden (`diff_sha` leer). Das ist eine offene Lücke gegenüber §9.1d.

## 3. Diff (line-level, §3)

Datei `kaggle/write_back_cycle.py` (rein Kaggle-Skript, kein `data/memory/`-Modul):

- `_load_tasks(zsre_file, n, seed)` → `_load_tasks(zsre_file, n, seed, *, split="train", exclude_questions=None)`.
  - **Interface-Änderung:** neue keyword-only Parameter, Default ändert den Split von `validation` auf `train` (Verhaltensänderung, durch Auftrag freigegeben).
- Neu: `_eval_questions(eval_file)` — liest Fragen (`messages[0].content`) aus Eval-JSONL; `None` → leere Menge; fehlende Datei → `FileNotFoundError` (laut).
- Neu: `select_tasks(records, n, seed, *, exclude_questions=None)` — reine Auswahl ohne Netz; Eval-Fragen werden **vor** Shuffle und Kappung entfernt.
- `main()`: neues CLI-Argument `--eval-file` (Default `None`); übergibt die Eval-Fragen als `exclude_questions`.
- Dateiname `zsre_validation.jsonl` bleibt bewusst (Schnittstellen-Stabilität, Guardrail 4). Der Inhalt ist jetzt Train-Split.
- Docstring-Zeile 8 nennt noch `split="validation"`; das ist veraltet und offen.

## 4. Drift (§5/§9.1d)

**Nicht gemessen.** Die Änderung ist nicht rein additiv (Default-Split geändert), daher ist `n/a` nicht zulässig. Ein Zeilen-Δ-Wert wurde nicht ermittelt. Kein `drift_index`-Tool in dieser Umgebung.

## 5. Tests (echt, ohne Netz)

`tests/test_heldout_split.py` — 5 Tests, alle grün (`pytest … -o addopts=""`, EXIT 0):

- ohne Ausschluss bleiben alle Zeilen (Abwärtskompatibilität),
- Ausschluss: `Overlap == 0`, Anzahl korrekt,
- Seed-Shuffle nach Ausschluss respektiert `n`,
- `_eval_questions` liest JSONL korrekt; `None` → leer,
- fehlende Eval-Datei bricht laut ab.

**Caveat:** Nur dieser Einzeltest lief. Die Gesamt-Coverage (100 % Gate, `pytest.ini`) wurde **nicht** über die komplette Suite geprüft. `kaggle/` ist nicht im `--cov`-Scope, daher ist die Abdeckung von `write_back_cycle.py` nicht gemessen.

## 6. Nicht behauptet

- Keine Θ′-Wirkung: der Kaggle-Lauf mit dem neuen Split ist **nicht** ausgeführt. Eine Wirkung wird nicht behauptet (§7).
- Die Baseline 20/20 & 8/8 ist ein Auftragsbeleg (HF-Datei), nicht lokal reproduziert.

## 7. Quellen

- Projekt: `kaggle/write_back_cycle.py`, `data/memory/approval.py` (`TwoPersonApproval`), `ergebnisse/zsre-eval-f6.jsonl`.
- AGENTS.md §9.1c/§9.3, Guardrail 1/4/7; Rek. 108/109/113.

## 8. Nächster Schritt

- P-A (Grader, strict + Extraktion/Base-Rate-Schutz).
- Docstring-Nachzug und Gesamt-Suite mit 100 % Coverage vor Abschluss.
- Echter Kaggle-Lauf mit `--eval-file` für den Split-Beleg.
