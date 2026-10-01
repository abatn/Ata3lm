# Test: Rekursionen (t=1 … t=5)

> Datum: 2026-09-30
> Zweck: Prüfung aller Rekursionen (Status, Score, Solver) + Validierungsset
> Lab-Prinzip: Keine Erfindungen – nur tatsächliche Dateiinhalte.

---

## 1. Rekursionen (t=1 … t=5)

| Rekursion | Datei | Freigabe-Status | π₀ (Compare) | π₁ (Akt) | Solver |
|---|---|---|---|---|---|
| t=1 | `008-t1-rekursion.md` | `pending` | — (Struktur-Check) | — | — |
| t=2 | `009-t2-echte-rekursion.md` | `approved: Batnini, 2026-09-30` | 1/3 | 3/3 | `solver.py` (sortiere_zahlen) |
| t=3 | `010-t3-rekursion.md` | `approved: Batnini, 2026-09-30` | 1/3* | 3/3 | `solver_v3.py` (finde_maximum) |
| t=4 | `011-t4-rekursion.md` | `pending` | 1/3* | 3/3 | `solver_v4.py` (berechne_durchschnitt) |
| t=5 | `012-t5-rekursion.md` | `pending` | 2/4 | 4/4 | `solver_v5.py` (finde_minimum) |

\* **Beobachtung (Lab-Prinzip: ehrlich):** In `010` und `011` nennt Zeile 31
„Score π₀ = 2/4", die Compare-Tabelle (Zeile 45) aber „Gesamt-Compare-Score: 1/3".
Das ist eine **interne Inkonsistenz** in diesen zwei Dateien (Zeile 31 vs. Zeile 45).
Der Compare-Score aus der Tabelle (1/3) ist der aus den 3 Testfällen berechnete Wert.

---

## 2. Solver-Dateien

| Datei | Aufgabe |
|---|---|
| `solver.py` / `solver_improved.py` | sortiere_zahlen |
| `solver_v3.py` / `solver_v3_improved.py` | finde_maximum |
| `solver_v4.py` / `solver_v4_improved.py` | berechne_durchschnitt |
| `solver_v5.py` / `solver_v5_improved.py` | finde_minimum |

**8 Solver-Dateien vorhanden** (4 buggy + 4 improved). ✅

---

## 3. Validierungsset (`ergebnisse/rekursion/validierungsset/`)

**16 Dateien** total:
- 3 Meta: `01-struktur-check.md`, `02-connector-reference.md`, `03-quellen-link-check.md`
- 12 Solver-Testfälle:
  - `04–06`: solver (sortiere_zahlen) – 3 Tests
  - `07–09`: solver_v3 (finde_maximum) – 3 Tests
  - `10–11`: solver_v4 (berechne_durchschnitt) – 2 Tests
  - `12–15`: solver_v5 (finde_minimum) – 4 Tests
- 1 `README.md`

**12 Testfälle** + 3 Meta + 1 README = 16. ✅

---

## 4. Zusammenfassung

| Prüfung | Ergebnis |
|---|---|
| Rekursionen t=1…t=5 vorhanden | ✅ (5/5) |
| Freigaben | 2 approved (t=2,t=3), 3 pending (t=1,t=4,t=5) |
| Solver-Dateien | ✅ 8 |
| Validierungsset | ✅ 16 Dateien (12 Testfälle) |
| **Interne Inkonsistenz** | ⚠️ `010`/`011` Zeile 31 (2/4) vs. Zeile 45 (1/3) |

**Fazit:** Alle 5 Rekursionen, 8 Solver und das Validierungsset existieren.
**Offener Punkt:** In `010-t3` und `011-t4` widerspricht Zeile 31 („Score π₀ = 2/4")
der Compare-Tabelle (1/3) – zu korrigieren.
