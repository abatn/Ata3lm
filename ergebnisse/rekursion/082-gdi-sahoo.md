# Rekursion 082: Goal Drift Index (GDI) – exakt nach arXiv:2603.06333 (Gl. 5–16)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare → Revise (echte Tests).
> Ziel `g`: den **Goal Drift Index (GDI)** genau nach der offiziellen Quelle
> arXiv:2603.06333 (Appendix B, Gl. 5–16) additiv in `data/memory/bias_monitor.py`
> ergänzen – **ohne Erfindung** und ohne die bestehende JSD-`BiasDriftMonitor`
> (WhyLab/Agent-Drift) zu entfernen.
> Quelle: <https://arxiv.org/abs/2603.06333> (SAHOO, ICLR-2026-Workshop; in
> `AGENTS.md` §9.1c zitiert ⇒ **keine neue Quelle**, kein Ontologie-Eintrag).
> Status: **umgesetzt** · §9-Status: **`approved` (Batnini + Taoufik, 2026-10-08)** ·
> **kein Commit** (G6).

## 1. Soll / Norm (Quelle wörtlich als Spezifikation)

| Gl. | Formel (Quelle arXiv:2603.06333, Appendix B) |
|---|---|
| 5/6 | normierte Embeddings `ê = e / (||e|| + ε)` |
| 7 | `s_cos = ê_0 · ê_t` (Kosinus) |
| 8 | **Semantic** `Δ_sem = (1 − s_cos) / 2` (Bereich [0,1]) |
| 9 | **Lexical** `Δ_lex = JSD(P_0‖P_t) = ½·KL(P_0‖M) + ½·KL(P_t‖M)`, `M = ½(P_0+P_t)` (Basis 2, [0,1]) |
| 10 | **Structural** `Δ_struct = (1/K)·Σ_k min(1, |s0_k − st_k| / (s0_k + ε))` |
| 11 | **Distributional** `Δ_dist = W(P_baseline, P_current)` = 1-Wasserstein (1-D) |
| 12 | **GDI** `= w_s·Δ_sem + w_l·Δ_lex + w_st·Δ_struct + w_d·Δ_dist` |
| 13 | `w_s + w_l + w_st + w_d = 1`, `w_i ∈ [0,1]` |
| 14 | Gewichte lernen `w* = argmax_w Σ_i AUC(GDI_i(w), y_i^drift)` (`y_i^drift ∈ {0,1}`) |
| 15 | Schwelle lernen `τ* = argmax_τ F1(GDI > τ, y^drift)` |
| 16 | 95%-CI = empirische **0.025**- und **0.975**-Quantile von `B` Bootstrap-Replikaten (Haupttext `B≈2000`) |

Referenz-Gewichte (Haupttext, Tabelle): **sem 0.38 · dist 0.29 · struct 0.21 · lex 0.12**.

Norm: `AGENTS.md` §9.1c (Drift-Bound; „Drift-Thresholds **kalibriert**, nicht
willkürlich") · §6 (keine Erfindungen) · Guardrail 7 (echte Verifikation).
**Belegt** sind ausschließlich die Formeln/Verfahren Gl. 5–16; die
**Default-Gewichte** des Haupttexts sind **Auftrag**.

## 2. Ist vorher (Lücke)

- `data/memory/bias_monitor.py` enthielt **nur** die JSD-basierte
  `BiasDriftMonitor` + Helfer (`entropy`, `jsd`, `capped_simplex`,
  JSD-`drift_index`) – Quelle WhyLab/Agent-Drift (arXiv:2601.04170).
- **Fehlend:** Semantic-/Lexical-/Structural-/Distributional-Drift als
  Einzelmaße, GDI-Aggregation (Gl. 12–13), AUC-Gewichts- (Gl. 14) und
  F1-τ-Kalibrierung (Gl. 15), Bootstrap-CI (Gl. 16).

## 3. Diff (line-level, additiv – 0 Löschungen)

```diff
 # data/memory/bias_monitor.py
+import random
+
+_WEIGHT_KEYS = ("sem", "lex", "struct", "dist")
+DEFAULT_WEIGHTS = {"sem": 0.38, "lex": 0.12, "struct": 0.21, "dist": 0.29}  # Auftrag
+
+def semantic_drift(e0, et, eps=1e-12): ...      # Gl. 5–8
+def _to_dist(x): ...                             # Gl. 9 (Dict/Tokenliste → Verteilung)
+def lexical_drift(p0, pt): ...                   # Gl. 9 (JSD, Basis 2)
+def structural_drift(s0, st, eps=1e-12): ...     # Gl. 10 (min-Cap)
+def distributional_drift(sample0, samplet): ...  # Gl. 11 (1-D-Wasserstein, closed form)
+def gdi(sem, lex, stru, dist, weights=None): ... # Gl. 12–13
+def calibrate_weights(scores, labels, grid=None): ...  # Gl. 14 (AUC, Rang-Statistik)
+def calibrate_tau(gdi_values, labels): ...       # Gl. 15 (F1-max)
+def bootstrap_ci(values, B=2000, alpha=0.05): ...# Gl. 16
```

| Datei | Inhalt |
|---|---|
| `data/memory/bias_monitor.py` | +238 Zeilen (0 entfernt): GDI-Block + erweiterter Modul-Docstring (Quelle Gl. 5–16, Belegt-vs-Auftrag, Paper-Inkonsistenz). Bestehende `BiasDriftMonitor` **unverändert**. |
| `tests/test_bias_monitor_gdi.py` | **neu**: 35 echte, handgerechnete Fälle (Gl. 8/9/10/11/12/13/15/16, AUC, Gitter). |
| `ergebnisse/rekursion/README.md` | +1 Index-Zeile (082). |

- Geänderte Komponenten: **1** (`bias_monitor.py`).
- Interface-/Format-Änderung? **additiv** (neue Funktionen); kein bestehendes
  Interface geändert ⇒ rückwärtskompatibel. Gate dennoch **`approved`** (§9,
  siehe §7 – Drift > Bound).

## 4. Ehrliche Grenzen (keine Erfindung)

- **Paper-Inkonsistenz Gl. 14 (dokumentiert, nicht aufgelöst):** Gl. 14 schreibt
  `argmax_w Σ_i AUC(…)` vor; der begleitende Haupttext nennt daneben „logistic
  regression". Implementiert ist die **explizite Gleichung** (AUC über
  Rang-/Paar-Statistik, kein sklearn) – der Widerspruch wird nicht geraten.
- **Numerischer Schwellwert `0.44`: nicht gefunden.** In der zitierten Quelle
  (Gl. 5–16) existiert **kein** konkreter τ-Zahlenwert; Gl. 15 definiert τ nur
  als F1-Maximierer. `0.44` wurde daher **nicht** implementiert/geraten.
- **Bootstrap-Statistik (Gl. 16):** Die Gleichung legt nur Quantile (0.025/0.975)
  und `B` fest; die **Statistik je Replikat** wird nicht benannt („nicht
  gefunden") – hier der Mittelwert, im Docstring kenntlich gemacht.
- **Default-Gewichte** `0.38/0.12/0.21/0.29` = Auftrag (Haupttext-Tabelle), im
  Code als `DEFAULT_WEIGHTS` markiert.

## 5. Compare / Beleg (externes Signal: echte Tests)

```text
pytest tests/test_bias_monitor_gdi.py -q --no-cov -p no:cacheprovider   -> 35 passed
pytest -m "not network and not live" -q --no-cov -p no:cacheprovider    -> 620 passed, 27 deselected
ruff check data/memory/bias_monitor.py tests/test_bias_monitor_gdi.py   -> All checks passed
ruff format --check data/memory/bias_monitor.py tests/test_bias_monitor_gdi.py -> 2 files already formatted
Coverage data/memory/bias_monitor.py (Line + Branch)                    -> 100 % (207 Stmts, 72 Branch, 0 Miss)
```

Coverage-Kommando (exakt): `pytest tests/test_bias_monitor_gdi.py tests/test_memory.py
-o addopts="" -q --cov=bias_monitor --cov-branch --cov-report=term-missing`.

Handgerechnete Anker (Auszug, kein Fake):
`semantic_drift`: cos 1/0/−1 ⇒ 0/0.5/1 · `lexical_drift`: JSD(P,P)=0, disjunkt=1 ·
`structural_drift`: identisch=0, |Δ|≥s0 ⇒ 1 · `distributional_drift`: identisch=0,
Verschiebung um 1 ⇒ 1 · `gdi` Default ⇒ 2,41 · `calibrate_tau([0.1,0.4,0.6,0.9],[0,0,1,1])` ⇒ τ=0.4, F1=1.0 ·
`bootstrap_ci` konstant ⇒ CI=Punktwert.

## 6. Drift (Δ zur Baseline, §9.1c)

| Artefakt | geänderte Zeilen (numstat: +/−) | Dateizeilen | Roh-Anteil |
|---|---|---|---|
| `bias_monitor.py` | +238 / −0 | 411 | ~57,9 % |

- Roh-Anteil liegt **über** dem 10 %-Default des §9.1c ⇒ **Human-Gate (ask)**
  erforderlich. Es handelt sich um rein **additiven** Code (neue Funktionen +
  Docstring), keine Änderung an `AGENTS.md`/`data/memory/tier1-base/` und keine
  Änderung bestehender Signaturen.
- **Gate-Anbindung:** Die Überschreitung ist durch die **Zwei-Personen-Freigabe**
  (§9.3) abgedeckt.

## 7. §9-Gate

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score (Tests) | `0/35 → 35/35` = `0 % → 100 %` | automatisch (nur repro) |
| Neue Quelle? | nein (arXiv:2603.06333 ist via §9.1c zitiert) | — |
| Interface-Änderung | nein (additiv, rückwärtskompatibel) | — |
| Drift ≤ Bound? | **nein** (~57,9 % > 10 %, §9.1c) | **ask → `approved`** |
| self_update an Originaldatei? | nein | — |

- **Gate-Ergebnis:** Drift > Bound ⇒ `ask` ⇒ **`approved`** (Batnini + Taoufik,
  2026-10-08, §9.3: ≥ 2 distinkte Personen).
- **Kein Commit** (Guardrail 6). Reviewer-Kommandos: `git status --short`, `git diff --stat`.

**§9-Status: `approved` (Batnini + Taoufik, 2026-10-08).**

## 8. Nächstes Self-Feedback (t+1)

- `calibrate_weights` (Gl. 14) ist implementiert, aber **noch nicht** auf echte
  Drift-Labels kalibriert (kein kalibrierter Datensatz im Repo) – die
  Referenz-Gewichte (Auftrag) bleiben Default. t+1-Frage: liegen
  `(Score-Vektor, y^drift)`-Paare vor, um `DEFAULT_WEIGHTS` durch `w*` zu ersetzen?
- Der numerische τ-Wert bleibt offen (Quelle nennt keinen) – `calibrate_tau`
  liefert τ datengetrieben aus Gl. 15; eine feste 0.44 wird **nicht** erfunden.
