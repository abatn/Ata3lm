# Rekursion 083: Kalibrier-Harness für den Drift-Schwellwert (Gl. 14–16)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare → Revise (echte Tests).
> Ziel `g`: einen **quellen-basierten Kalibrier-Harness** für den Drift-Schwellwert
> bauen, der die vorhandenen GDI-Primitive (Gl. 8–16 aus
> `data/memory/bias_monitor.py`) zu Textpaaren, externem Grader-Label und
> `calibrate(...)` verdrahtet – **ohne Erfindung**, mit **externem
> Grader-Signal (§6)** als Label-Ersatz für die Experten-Annotation des Papers.
> Quelle: <https://arxiv.org/abs/2603.06333> (SAHOO, ICLR-2026-Workshop; in
> `AGENTS.md` §9.1c zitiert ⇒ **keine neue Quelle**).
> Status: **umgesetzt** · §9-Status: **`approved` (Batnini + Taoufik, 2026-10-08)** ·
> **kein Commit** (G6).

## 1. Soll / Norm (Quelle wörtlich als Spezifikation)

| Gl. | Formel (Quelle arXiv:2603.06333, Appendix B) | Umsetzung |
|---|---|---|
| 8–11 | Semantic `Δ_sem=(1−s_cos)/2`, Lexical `Δ_lex=JSD`, Structural `Δ_struct=(1/K)Σ min(1,|Δs|/(s0+ε))`, Distributional `Δ_dist=W` | `bias_monitor` (vorhanden, 082) – `signal_vector` ruft sie je Textpaar auf |
| 12–13 | `GDI = Σ w_i·Δ_i`, `Σw=1`, `w_i∈[0,1]` | `gdi_of` → `bias_monitor.gdi` |
| 14 | `w* = argmax_w Σ_i AUC(GDI_i(w), y_i^drift)`; Labels „obtained via expert annotation during calibration" | `calibrate` → `bias_monitor.calibrate_weights` |
| 15 | `τ* = argmax_τ F1(GDI > τ, y^drift)` | `calibrate` → `bias_monitor.calibrate_tau` |
| 16 | 95%-CI = **0.025/0.975**-Quantile von `B≈2000` Bootstrap-Replikaten | `calibrate` → `bias_monitor.bootstrap_ci` |

Norm: `AGENTS.md` §9.1c (Drift-Thresholds **kalibriert**, nicht willkürlich) ·
§6 (keine Erfindungen) · Guardrail 7 (echte Verifikation).

**Status-Trennung (im Modul-Docstring):**
- **Belegt:** Gl. 8–16 – ausschließlich die Formeln/Verfahren der Quelle.
- **Auftrag (§6):** Das Paper nutzt **Experten-Annotation** für `y^drift`; hier
  ersetzt ein **externes Grader-Signal** (Grader/Code-Run/DB,
  `world_state_oracle`) dieses Label. Mapping gesetzt: Grader „bestanden"
  (kein Drift) ⇒ `y_drift = 0`, sonst `1`.
- **Auftrag:** Struktur-Features (Gl. 10) = Länge, Zeilenzahl,
  Codeblock-Anzahl, Listenpunkte; distributional-Sample (Gl. 11) = auf den
  gemeinsamen Maximalwert normierte Zeilen-Tokenzahlen. Die Quelle legt beides
  nicht fest.

## 2. Ist vorher (Lücke)

- `bias_monitor.py` (Rekursion 082) liefert die **Primitive**: `semantic_drift`,
  `lexical_drift`, `structural_drift`, `distributional_drift`, `gdi`,
  `calibrate_weights` (Gl. 14), `calibrate_tau` (Gl. 15), `bootstrap_ci` (Gl. 16).
- `world_state_oracle.evaluate` + `evaluator_version` liefern das **externe
  Signal** (§6).
- **Fehlend:** die Verdrahtung von **Text → Signal-Vektor → GDI → Kalibrierung**
  mit **injizierbaren** `embed_fn`/`grader_fn` – d. h. ein Harness, der Gl. 14–16
  aus Textpaaren + externem Grader-Signal ausführt und `{weights, tau, ci, n, note}`
  liefert.

## 3. Diff (additiv – keine Löschung, keine Signaturänderung)

| Datei | Inhalt |
|---|---|
| `data/memory/drift_calibration.py` | **neu** (240 Zeilen): `signal_vector` (Gl. 8–11 je Textpaar), `gdi_of` (Gl. 12–13), `collect_samples` (Gl. 12–14), `calibrate` (Gl. 14–16), `structural_features` (Auftrag), `_distributional` (Auftrag), lazy `_default_grader_fn` (§6). |
| `tests/test_drift_calibration.py` | **neu** (162 Zeilen): 14 deterministische Stub-Tests (echte Mathematik, kein Netz). |
| `ergebnisse/rekursion/README.md` | +1 Index-Zeile (083). |

- Geänderte **bestehende** Komponenten: **0** (bias_monitor, world_state_oracle,
  evaluator_version unberührt).
- Interface-/Format-Änderung? **nein** (neues, additives Modul; keine bestehende
  Signatur geändert).
- `embed_fn`/`grader_fn` sind **injizierbar**; der Default-Grader
  (`world_state_oracle` + `evaluator_version`, echter LLM/Netz-Aufruf) wird
  **lazy** gebaut und im Unit-Test **nicht** aufgerufen (Guardrail 7).

## 4. Ehrliche Grenzen (keine Erfindung)

- **τ wird hier NICHT gesetzt.** `calibrate` liefert `τ*` datengetrieben nach
  Gl. 15, aber der **echte Kalibrierlauf** mit externem Grader-Signal (§6) ist
  **separat** und nicht Teil dieser Aufgabe. Der Harness ist die Mechanik, das
  Label im Test ein deterministischer **Stub**.
- **Experten-Annotation ersetzt:** Das Paper verlangt `y^drift` „via expert
  annotation during calibration"; implementiert ist ein **externes
  Grader-Signal** (§6) – als **Auftrag** gekennzeichnet, kein Paper-Claim.
- **Gl.-16-Statistik:** Die Quelle benennt die Statistik je Bootstrap-Replikat
  nicht (siehe 082); `bootstrap_ci` nutzt den **Mittelwert** – im `note`-Feld
  kenntlich gemacht.
- **Struktur-Features / distributional-Sample:** Definition = Auftrag (die
  Quelle legt sie nicht fest).
- **Default-Grader** ist bewusst ungetestet (echter Netz-Aufruf); getestet ist
  nur seine **lazy Konstruktion** (`callable`), nicht der Aufruf.

## 5. Compare / Beleg (externes Signal: echte Tests)

```text
pytest tests/test_drift_calibration.py -q --no-cov -p no:cacheprovider    -> 14 passed
pytest -m "not network and not live" -q --no-cov -p no:cacheprovider     -> 634 passed, 27 deselected
ruff check data/memory/drift_calibration.py tests/test_drift_calibration.py -> All checks passed
ruff format --check data/memory/drift_calibration.py tests/test_drift_calibration.py -> 2 files already formatted
Coverage data/memory/drift_calibration.py (Line + Branch)                 -> 100 % (76 Stmts, 16 Branch, 0 Miss)
```

Coverage-Kommando (exakt): `pytest tests/test_drift_calibration.py -o addopts=""
-q --cov=drift_calibration --cov-branch --cov-report=term-missing -p no:cacheprovider`.

Handgerechnete Anker (Auszug, kein Fake):
`signal_vector` aller Signale ∈ [0,1] (normiertes distributional-Sample) ·
identische Texte ⇒ `sem/lex/struct/dist = 0` · leere Texte ⇒ `Δ_sem = 0.5` (Nullvektor,
Gl. 5–8), sonst 0 · `collect_samples` liefert `len == n` und Labels `[0,1]` aus dem
Stub-Grader · konstruiertes Trennbeispiel: identische „quiet"-Paare ⇒ GDI 0 (Label 0),
disjunkte „loud"-Paare ⇒ GDI > 0 (Label 1) ⇒ `F1 = 1.0`, `min(pos) > τ* ≥ max(neg)` ·
`calibrate([])` ⇒ Default-Gewichte, `τ = 0.0`, CI `[0,0]`.

## 6. Drift (Δ zur Baseline, §9.1c)

| Artefakt | Zeilen (neu) | Bezug | Roh-Anteil |
|---|---|---|---|
| `data/memory/drift_calibration.py` | +240 | neue Datei | additiv (kein Bestand geändert) |
| `tests/test_drift_calibration.py` | +162 | neue Datei | additiv |
| `ergebnisse/rekursion/README.md` | +1 | Bestand | < 1 % |

- **0 bestehende Zeilen geändert** (nur additive neue Dateien + 1 Index-Zeile).
  Die Roh-Änderung an Bestandsdateien (< 1 %) liegt **unter** dem 10 %-Default;
  die rein additive System-Erweiterung wird dennoch per Human-Gate geprüft
  (Interface-Erweiterung ⇒ §9 „ask").
- **Gate-Anbindung:** Überschreitung nicht einschlägig; Freigabe durch die
  **Zwei-Personen-Freigabe** (§9.3) abgedeckt.

## 7. §9-Gate

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score (Tests) | `0/14 → 14/14` = `0 % → 100 %` | automatisch (nur repro) |
| Neue Quelle? | nein (arXiv:2603.06333 ist via §9.1c zitiert) | — |
| Interface-Änderung | nein (neues additives Modul) | — |
| Drift ≤ Bound? | ja (0 bestehende Zeilen geändert) | automatisch |
| self_update an Originaldatei? | nein | — |

- **Gate-Ergebnis:** rein additiv, keine neue Quelle, kein `self_update` an
  Originaldateien ⇒ automatisch erlaubt; zusätzlich **`approved`**
  (Batnini + Taoufik, 2026-10-08, §9.3: ≥ 2 distinkte Personen).
- **Kein Commit** (Guardrail 6). Reviewer-Kommandos: `git status --short`, `git diff --stat`.

**§9-Status: `approved` (Batnini + Taoufik, 2026-10-08).**

## 8. Nächstes Self-Feedback (t+1)

- Der **echte Kalibrierlauf** mit externem Grader-Signal (§6) gegen einen
  `evaluator_version`-Anker steht aus; erst dann wird `τ*` real gesetzt und
  `DEFAULT_WEIGHTS` durch `w*` ersetzt. Der Harness ist dafür die Schnittstelle.
- Offene, ehrlich benannte Punkte: Gl.-16-**Statistik** (Quelle schweigt),
  Struktur-Features/distributional-Sample (Auftrag), Default-Grader (Netz).
