# Rekursion 093: Kalibriertes GDI (SAHOO Gl. 12–16) im Betriebspfad (Item 3)

> Datum: 2026-10-09 · Phasen: Konstrukt → Akt → Observe → Compare → Revise.
> Ziel `g` (§2/§9.1c): Der Betrieb nutzt das **kalibrierte** Drift-Gate
> (`ergebnisse/drift-calibration-sahoo.json`: `tau`, `weights`) – nicht mehr die
> feste JSD-Schwelle `tau=0.10`. Quellen (**Belegt**, in `AGENTS.md` §9.1c
> referenziert ⇒ **keine neue Quelle**): **arXiv:2603.06333 (SAHOO)** Gl. 12–16
> (GDI-Aggregation, AUC-/F1-Kalibrierung, Bootstrap-CI); die Kalibrier-Werte
> liegen bereits vor (Rekursion 082/083/085/088). Status: **`approved`**
> (§9-Freigabe Batnini + Taoufik, 2026-10-08) – **Interface-Änderung**,
> kenntlich gemacht. Kein `self_update` an `AGENTS.md`/`tier1-base`.

## 1. Soll (Belegt + Auftrag)

- **Belegt (arXiv:2603.06333 Gl. 12–13):** `GDI = Σ_k w_k · Δ_k` mit den
  kalibrierten Gewichten `w*`; **Gl. 14** `w* = argmax_w Σ_i AUC(GDI_i(w), y_i^drift)`;
  **Gl. 15** `τ* = argmax_τ F1(GDI > τ, y^drift)`; **Gl. 16** 95%-CI.
- **Auftrag (§9.1c):** Drift-Schwelle = **kalibriert**, nicht willkürlich. Die
  Implementierung der Primitive (`gdi`, `calibrate_weights`, `calibrate_tau`,
  `bootstrap_ci`) und der Signal-Vektor (`drift_calibration.signal_vector`)
  existiert bereits (Rekursion 082/083) – **bisher aber nicht im Betriebspfad**:
  `BiasDriftMonitor.observe` nutzt ausschließlich JSD mit festem `tau=0.10`.
- **Auftrag (Item 3):** Diese Lücke schließen – **additiv** und
  **rückwärtskompatibel**.

## 2. Ist (vorher → nachher)

| Ort | Vorher | Nachher |
|---|---|---|
| `bias_monitor` | nur `observe` (JSD, `tau=0.10`) | + `load_calibration(path=None)` liest `drift-calibration-sahoo.json`; + `BiasDriftMonitor`-Felder `gdi_weights`/`gdi_tau`; + `observe_gdi(...)` |
| `lifecycle_runner` | Stufe 8 immer `observe` (JSD) | + Schalter `gdi=False` / `embed_fn` / `gdi_calibration` / `gdi_prev_text`; Stufe 8 nutzt bei Aktivierung `observe_gdi` |

**Fallback (Auftrag):** fehlt die Kalibrierungsdatei, ist sie ungültig, fehlt
`embed_fn`/Referenztext oder der Schalter `gdi` → **exakt altes JSD-Verhalten**
(Default `gdi=False`), **kein Crash**.

## 3. Umsetzung (Interface-Änderung §9 approved)

- `data/memory/bias_monitor.py`:
  - `CALIBRATION_PATH` = repo-root/`ergebnisse/drift-calibration-sahoo.json`
    (modulrelativ, cwd-unabhängig).
  - `load_calibration(path=None)`: liest JSON, validiert Gewichte via
    `_resolve_weights` (Gl. 13) + `float(tau)`; `OSError`/`ValueError`/`TypeError`/
    `KeyError`/`AttributeError` ⇒ `None` (JSD-Fallback).
  - `BiasDriftMonitor` + optionale Felder `gdi_weights=None`, `gdi_tau=None`
    (Defaults ⇒ bisheriges Verhalten unverändert).
  - `observe_gdi(prev_text, cur_text, *, embed_fn, step=None)`: ruft
    `drift_calibration.signal_vector` (Gl. 8–11) → `gdi(..., weights=kalibriert)`
    (Gl. 12–13); flaggt gegen das kalibrierte `τ` (`gdi_tau`, sonst `self.tau`);
    Rückgabe `{"step","gdi","flagged","gate","weights","tau"}`. Lazy-Import
    vermeidet den Zyklus `bias_monitor ↔ drift_calibration`.
  - `report()` liest GDI-Records robust (`h.get("DI", 0.0)`).
- `data/memory/lifecycle_runner.py`:
  - `run_cycle(...)` + optionale Parameter `gdi=False`, `embed_fn=None`,
    `gdi_calibration=None`, `gdi_prev_text=None` (alle keyword-only).
  - Aktivierungsbedingung: `gdi and embed_fn is not None and gdi_prev_text is not None
    and kalibrierung is not None`; Kalibrierung = `gdi_calibration` oder
    `bias_monitor.load_calibration()`.
  - Stufe 8 (`_stage_wissen_plus`) zweigt bei `gdi_enabled` auf `observe_gdi`
    (`reference="gdi"`); sonst unveränderter JSD-Pfad (inkl. Checkpoint-Logik).
  - **Kein Checkpoint-Write im GDI-Modus** (die Referenz ist Text, nicht die
    Label-Verteilung) – kenntlich gemacht, keine erfundene Text-Semantik.

## 4. Diff (erwartet; `git status --short`/`--stat` siehe unten)

```
 data/memory/bias_monitor.py            | +58/-4   (load_calibration, observe_gdi, Felder)
 data/memory/lifecycle_runner.py        | +40/-2   (GDI-Schalter, Stufe-8-Zweig)
 tests/test_gdi_betrieb.py              | neu       (9 Tests)
 ergebnisse/rekursion/093-gdi-betrieb.md| neu       (diese Datei)
 ergebnisse/rekursion/README.md         | +1        (Index-Zeile 093)
```

- `AGENTS.md` und `data/memory/tier1-base/` **nicht** geändert (Guardrail 6,
  §9.1b). Keine neue Quelle.

## 5. Compare / Tests (offline, echtes Test-Signal)

Neues Repro (`tests/test_gdi_betrieb.py`, offline mit injizierter `embed_fn` +
Kalibrierung; Guardrail 7 – **kein** Netz/Endpoint):

| Test | Aussage |
|---|---|
| `test_load_calibration_liest_echte_json` | liest echtes `{"tau","weights"}` aus tmp |
| `test_load_calibration_default_pfad_ist_echte_datei` | `path=None` liest die Repo-Datei (τ>0, Σw=1) |
| `test_load_calibration_fehlt_ist_none` | fehlende Datei ⇒ `None` (JSD-Fallback) |
| `test_load_calibration_ungueltig_ist_none` | kaputtes JSON / fehlendes τ / unvollständige Gewichte / kein Dict ⇒ `None` |
| `test_observe_gdi_niedrig_allow_hoch_ask` | niedriger GDI `< τ` ⇒ `allow`; hoher `> τ` ⇒ `ask`; nutzt die **geladenen Gewichte** |
| `test_observe_gdi_defaults_ohne_kalibrierung` | ohne Kalibrierung ⇒ Default-Gewichte + `self.tau` |
| `test_lifecycle_default_gdi_aus_identisch` | Default (`gdi=False`) verhaltensgleich zum JSD-Pfad, keine GDI-Keys |
| `test_lifecycle_gdi_an_nutzt_kalibriertes_tau` | mit GDI an greift das kalibrierte τ (0.24) in Stufe 8 |
| `test_lifecycle_gdi_fallbacks_jsd` | fehlt `embed_fn` / Referenztext / Kalibrierung ⇒ JSD-Fallback |

**Akzeptanz (ausgeführt):**

- `.venv/bin/python -m pytest tests/test_gdi_betrieb.py -q --no-cov` → **9 passed**.
- `.venv/bin/python -m pytest -m "not network and not live" -q --no-cov -p no:cacheprovider`
  → **721 passed, 27 deselected**.
- Coverage `data/memory/bias_monitor.py` → **100 %** (232 Statements, 0 missed;
  72 Branches, 0 partial); `data/memory/lifecycle_runner.py` → **100 %**
  (172 Statements, 0 missed; 50 Branches, 0 partial).
- `ruff check` + `ruff format --check` (geänderte/neue Dateien) → sauber.

**Ehrlicher Hinweis (keine Erfindung):** Der Unit-Test nutzt einen
**Stub-`embed_fn`** (konstanter Vektor) – das echte Embedding (Endpoint,
Guardrail 7) wird im Unit-Test **nicht** aufgerufen; der semantische Anteil ist
im Test bewusst 0, das kalibrierte `lex`-Gewicht (0.85) ist das trennende Signal.
Das kalibrierte τ=0.240… stammt aus dem bereits committeten Lauf (Rekursion 088,
n=180); hier wird **nichts** neu kalibriert und **keine** Zahl erfunden.

## 6. §9-Gate

**`approved`** – §9-Freigabe Batnini + Taoufik, 2026-10-08. Die Änderung ist
eine **Interface-Änderung** von Bestandsmodulen (`BiasDriftMonitor`-Felder +
`observe_gdi`; `run_cycle`-Parameter) – kenntlich gemacht. Alle neuen Parameter
haben **rückwärtskompatible Defaults** (`None`/`False`) ⇒ Default-Verhalten
unverändert. Keine neue Quelle (SAHOO + `signal_vector` bereits in §9.1c / §10
verankert), kein `self_update` an Originaldateien. `data/`-Dateien/Test ⇒
**kein** `versions/vN`. **Kein** `git add/commit/push` (Guardrail 6);
`git status --short`/`diff --stat` siehe unten.
