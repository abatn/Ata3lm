# Rekursion 080: N7 — Oracle-Evidenz entscheidet die Revision (nicht der Selbstreport)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare → Revise (echte Tests).
> **Befund-Quelle (verbindlich): Audit b09a0a9** (Datei `tests/test_network_boundaries.py`).
> N-Nummerierung = **Audit** (NICHT Rekursion 062–063).
> Ziel `g`: Bei gesetztem `world_state_probe` fließt die **Oracle-Evidenz** in die
> Revisionsentscheidung ein – Compare und Revise stützen sich auf **dieselbe**
> externe Quelle (§6); der Selbstreport (`successes`/`failures`) ist nur Annotation.
> Auftrag: „Knowledge-Agent härten — N1–N8 (Revision b09a0a9)", **Phase 2** (Fix N7).
> Status: **umgesetzt** · §9-Status: **`approved` (Batnini + Taoufik, 2026-10-08)** ·
> **kein Commit** (G6).

## 1. Soll/Norm (Audit + Fundstellen)

| Feld | Wert (Audit b09a0a9, verbindlich) |
|---|---|
| Befund N7 | **N7 · P2 · Oracle-Compare vs. Revise: gleiche Evidenz** |
| Datei | `data/memory/recursion_runner.py` (`_phase_compare` ~`:104-126`, `_phase_revise` ~`:164-179`) |
| **Soll** | Ist ein `world_state_probe` gesetzt, entscheidet die **Oracle-Evidenz** die Revision; der Selbstreport ist nur Annotation. Ohne Probe bleibt der bisherige Pfad unverändert. |
| Repro N7 | `test_oracle_success_drives_revision_without_self_report` |

Norm: `AGENTS.md` §6 („Compare nur mit externem Signal … sonst konfidente
Fehlanpassung") · §9.1d/R10 (nur mit passender Evidenz und Score ≥ 70 %) ·
Regel 9 (Gate-Band `allow|ask|deny`). Mechanik der Out-of-Band-Evaluation:
`world_state_oracle.py` (Rekursion 073, Quelle arXiv:2607.25152 – bereits im Repo).

## 2. Befund (Ist ≠ Soll)

- `_phase_compare` wertet bei gesetztem `world_state_probe` das **Out-of-Band-Ergebnis**
  (`world_state_oracle.evaluate`) aus und meldet `observed`/`score`/`gate`/`oracle`.
- `_phase_revise` rechnete `score`/`evidence_ok` aber ausschließlich aus dem
  **Selbstreport** (`ctx["successes"]`/`ctx["failures"]`).
- **Folge:** Ein Oracle-Erfolg (`observed=True`, Compare `allow`) bei
  `successes=failures=0` (Selbstreport) führte in Revise zu `evidence_ok=False`
  ⇒ Revision verweigert. Compare und Revise nutzten **verschiedene** Evidenzquellen
  (Verstoß gegen §6: „Compare nur mit externem Signal").

**Rot (HEAD-Modul, echter Repro-Lauf):**

```text
tests/test_network_boundaries.py::test_oracle_success_drives_revision_without_self_report
    assert out["results"]["Revise"]["skipped"] is False
E   assert True is False
1 failed
```

## 3. Änderung (Diff, line-level)

```diff
 # recursion_runner.py — _phase_revise (nach dem Akt-Zulässigkeits-Check)
-    n = ctx["successes"] + ctx["failures"]
-    score = (ctx["successes"] / n) if n else 0.0
-    # R10/A4: Score < 70 % ⇒ keine Revision (1 Erfolg / 99 Fehler lernt nicht).
-    evidence_ok = bool(vergleich.get("observed")) and ctx["successes"] >= 1 and score >= REVISE_MIN_SCORE
+    # N7/§6: Liegt ein Oracle-Signal vor (Compare mit `world_state_probe`), entscheidet
+    # die **Oracle-Evidenz** – Compare und Revise nutzen damit DIESELBE Quelle; der
+    # Selbstreport (`successes`/`failures`) ist nur Annotation.
+    oracle = vergleich.get("oracle")
+    if oracle is not None:
+        score = float(vergleich.get("score", 0.0))
+        positive = int(oracle.get("successes", 0)) >= 1
+    else:
+        n = ctx["successes"] + ctx["failures"]
+        score = (ctx["successes"] / n) if n else 0.0
+        positive = ctx["successes"] >= 1
+    # §9.1d/R10/A4: passende Evidenz = externes Signal mit ≥ 1 positivem Beleg und Score ≥ 70 %.
+    evidence_ok = bool(vergleich.get("observed")) and positive and score >= REVISE_MIN_SCORE
```

| Datei | Inhalt |
|---|---|
| `data/memory/recursion_runner.py` | `_phase_revise` bezieht `observed`/`score`/`oracle.successes` aus dem **Compare-Ergebnis**, wenn ein Oracle-Signal vorliegt; ohne Probe **byte-identische** Fortsetzung des Selbstreport-Pfads (§9.1d/R10 unverändert). |
| `tests/test_network_boundaries.py` | +1 verbindlicher Repro-Fall N7 (echter Datei-Oracle-Check), importiert `numpy`/`recursion_runner`. |
| `ergebnisse/proposal-f-n7.md` | Status → `implementiert (approved)`. |
| `ergebnisse/rekursion/README.md` | +1 Index-Zeile (080). |

- Geänderte Komponenten: **1** (`recursion_runner.py`).
- Interface-/Format-Änderung? **ja** — die Revisionsentscheidung wertet bei
  `world_state_probe` die Oracle-Evidenz statt des Selbstreports aus ⇒ §9-pflichtig,
  **`approved`** (Batnini + Taoufik, 2026-10-08).

## 4. Real vs. offen (ehrlich)

- **Real:** Der Repro-Probe ist ein **echter** Datei-Check (`marker.read_text() == "OK"`)
  – kein Mock, keine skriptete Antwort (Guardrail 7). Der Fall wurde zuerst **rot**
  gegen das HEAD-Modul verifiziert (§5), dann grün.
- **Rückwärtskompatibilität:** Ohne `world_state_probe` enthält das Compare-Ergebnis
  kein Feld `oracle` ⇒ `_phase_revise` läuft unverändert über den Selbstreport
  (`ctx["successes"] >= 1`, `score = successes/n`); alle bestehenden Revise-Tests
  (B6, R10, A4, deny/ask-Band) bleiben unverändert grün.
- **§9-Disziplin bleibt:** `deny` blockiert weiter, `ask` (70–94 %) nur mit
  `revise_approved`, Score < 70 % (R10) und fehlender positiver Beleg (§9.1d)
  verhindern die Revision – jetzt auf Basis der **Oracle**-Evidenz.
- **Kein `self_update`** an `AGENTS.md`/`data/memory/tier1-base/`; keine neuen
  externen Quellen; reale Stores unberührt.

## 5. Compare / Beleg (externes Signal: echte Tests)

**Rot (HEAD-Modul, echte Ausführung des Repro-Szenarios):**

```text
[OLD] N7 oracle : FAIL (Bug reproduziert)  # Compare allow (observed=True/score=1.0), Revise skipped=True
```

**Grün (neues Modul):**

```text
pytest tests/test_network_boundaries.py -k oracle_success --no-cov -q   -> 1 passed
pytest -m "not network and not live" -q --no-cov -p no:cacheprovider    -> 586 passed, 26 deselected
ruff check data/memory/recursion_runner.py tests/test_network_boundaries.py -> All checks passed
ruff format --check <4 Dateien>                                         -> 4 files already formatted
Coverage data/memory/recursion_runner.py (Line + Branch)                -> 100 % (99 Stmts, 32 Branch, 0 Miss)
```

Coverage-Kommando (exakt): `pytest -m "not network and not live" -o addopts="" -q
--cov=recursion_runner --cov-branch --cov-report=term-missing`.

Repro-Kommando (verbindlich): `pytest tests/test_network_boundaries.py -k oracle_success`.

## 6. Drift (Δ zur Baseline, §9.1c)

| Artefakt | geänderte Zeilen (numstat: +/−) | Dateizeilen | Roh-Anteil |
|---|---|---|---|
| `recursion_runner.py` | 15 + 5 = 20 | 365 | ~5,5 % |

- Roh-Anteil liegt **unter** dem 10 %-Default des §9.1c (inkl. Docstrings/Kommentaren).
- **Gate-Anbindung:** Drift ≤ Bound ⇒ kein zusätzliches Drift-Gate; die
  Interface-Änderung der Revisionsentscheidung ist durch die **Zwei-Personen-Freigabe**
  belegt.

## 7. §9-Gate

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score (repro) | `0/1 → 1/1` = `0 % → 100 %` | automatisch (nur repro) |
| Neue Quelle? | nein | — |
| Interface-Änderung (Revise-Evidenz) | **ja** | **ask → `approved`** |
| Drift ≤ Bound? | ja (≈ 5,5 % ≤ 10 %) | — |
| self_update an Originaldatei? | nein | — |

- **Gate-Ergebnis:** `ask` (Interface-Änderung) ⇒ **`approved`** (Batnini + Taoufik,
  2026-10-08, §9.3: ≥ 2 distinkte Personen).
- **Keine neue Quelle** (arXiv:2607.25152 / World-State-Oracle ist seit Rekursion 073
  in der Ontologie) ⇒ kein Human-Gate aus diesem Grund.
- **Kein Commit** (Guardrail 6). Reviewer-Kommandos: `git status --short`, `git diff --stat`.

**§9-Status: `approved` (Batnini + Taoufik, 2026-10-08).**

## 8. Nächstes Self-Feedback (t+1)

- `_phase_revise` nutzt jetzt bei Oracle-Signal `vergleich["score"]` + `oracle.successes`.
  Der degenerierte Fall `oracle={"ok": True, "successes": 0, "failures": 0}` (Compare
  vergibt per Fallback `score=1.0`, aber ohne positiven Zähler) bleibt in Revise
  konservativ blockiert (§9.1d „≥ 1 positiver Beleg"). Fließt in t+1: Soll Compare in
  diesem Fall `observed=True` ohne positiven Zähler überhaupt zulassen, oder soll der
  Fallback-Score an `oracle.ok` gekoppelt dokumentiert werden?
- Der Selbstreport wird in `Compare.self_report` weiterhin mitgeführt (Annotation) –
  eine spätere Anzeige/Drift-Metrik kann ihn auswerten, ohne die Revision zu steuern.
