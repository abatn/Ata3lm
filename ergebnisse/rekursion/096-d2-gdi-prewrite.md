# Rekursion 096: GDI-Gate VOR der Mutation (D2, Audit d25486c)

> Datum: 2026-10-09 · Phasen: Observe → Compare → Revise. Ziel `g` (§2/§9.1c):
> der **kalibrierte GDI** muss als **Schutzmechanismus VOR der Änderung** greifen
> (arXiv:2603.06333 Gl. 12–16) – **nicht erst** in Stufe 8/Wissen+. Quelle
> (**Belegt**, in `AGENTS.md` §9.1c referenziert ⇒ **keine neue Quelle**):
> **arXiv:2603.06333 (SAHOO)**; Werte/Mechanik bereits vorhanden (Rekursion
> 082/083/093). Status: **`approved`** (§9-Freigabe Batnini + Taoufik) –
> **Interface-Änderung**, kenntlich gemacht. Kein `self_update` an
> `AGENTS.md`/`tier1-base`.

## 1. Befund (D2, P1 aus Audit d25486c)

- **Soll (§9.1c/SAHOO Gl. 12–16):** GDI ist der Schutz gegen Drift **vor** dem
  Write. `gdi > τ ⇒ ask ⇒ KEIN Write`.
- **Ist (vorher):** Stufe 3 (`_stage_gedaechtnis`) schrieb via
  `pipeline.route_and_store` mit dem **JSD**-Gate; der **kalibrierte GDI** wurde
  erst in Stufe 8 (`_stage_wissen_plus`, `reference="gdi"`) berechnet. Damit
  konnte eine driftende Änderung **geschrieben** werden, bevor das GDI-Gate sie
  überhaupt sah (Schutz erst **nach** der Mutation).

## 2. Ist → Soll (Fix)

| Ort | Vorher | Nachher |
|---|---|---|
| `lifecycle_runner._stage_gedaechtnis` | nur `drift` (JSD) an die Store-Kette | bei `gdi_enabled`: **GDI zuerst** berechnen (`observe_gdi`) und als `gdi_drift` an die Store-Kette; `gdi > τ ⇒ ask ⇒ kein Write` |
| `pipeline.route_and_store` | reichte `drift` durch | + optionaler Parameter `gdi_drift` (Default `None`) → 1:1 an `write_gateway.store` |
| `write_gateway.store` | Drift-Gate (JSD) | + **Pre-Write-GDI-Gate** `gdi_drift` **vor** jeder Mutation; `gdi > τ ⇒ ask` |
| Stufe 8 `_stage_wissen_plus` | GDI-Revisionsfilter | **unverändert** – GDI wird zusätzlich weitergeführt (Revisionsfilter) |

**Default unverändert:** `gdi=False` ⇒ `gdi_enabled=False` ⇒ `gdi_drift=None` ⇒
exakt altes Verhalten (JSD-Pfad). Alle neuen Parameter sind **keyword-only** mit
Default `None`.

## 3. Umsetzung (Interface-Änderung §9 approved)

- `data/memory/lifecycle_runner.py` (`_stage_gedaechtnis`): wenn
  `ctx["gdi_enabled"]` (gdi + `embed_fn` + Referenztext + Kalibrierung, bereits
  in `run_cycle` bestimmt), wird
  `gdi_monitor.observe_gdi(gdi_prev_text, fact, embed_fn=..., step=1)` **vor**
  `route_and_store` berechnet und als `gdi_drift=...` übergeben.
- `data/memory/pipeline.py` (`route_and_store`): neuer optionaler Parameter
  `gdi_drift=None`, durchgereicht an `write_gateway.store`.
- `data/memory/write_gateway.py` (`store`): neuer optionaler Parameter
  `gdi_drift=None`; Prüfung **nach** dem JSD-Drift-Gate und **vor** Record/Write:
  `gate = normalize(gdi_drift["gate"])`; `not is_allow(gate)` ⇒ Rückgabe
  `ok=False`, `gate`, `action`, **`written=[]`** (keine Mutation, keine
  Provenienz-Zeile).
- **Kein** Checkpoint-Write im GDI-Modus (Referenz = Text) – wie Rekursion 093.

## 4. Diff (erwartet; `git status --short`/`--stat` siehe unten)

```
 data/memory/lifecycle_runner.py        | +15     (_stage_gedaechtnis: GDI pre-write)
 data/memory/pipeline.py                | +7      (gdi_drift durchreichen)
 data/memory/write_gateway.py           | +28     (gdi_drift Pre-Write-Gate)
 tests/test_d2_gdi_prewrite.py          | neu     (4 Tests)
 ergebnisse/rekursion/096-d2-gdi-prewrite.md | neu (diese Datei)
 ergebnisse/rekursion/README.md         | +1      (Index-Zeile 096)
```

- `AGENTS.md` und `data/memory/tier1-base/` **nicht** geändert (Guardrail 6,
  §9.1b). Keine neue Quelle.

## 5. Compare / Tests (offline, echtes Test-Signal)

Neues Repro (`tests/test_d2_gdi_prewrite.py`, offline mit injizierter `embed_fn`
+ Kalibrierung; Guardrail 7 – **kein** Netz/Endpoint):

| Test | Aussage |
|---|---|
| `test_gdi_over_tau_blocks_write_before_mutation` | `GDI > τ` (0.85 > 0.24) ⇒ `ask` ⇒ **kein** Structured-/tier3-File, **keine** Provenienz-Zeile; `Wissen+` `revised=False` |
| `test_gdi_under_tau_allows_write` | `GDI ≤ τ` (0.0) ⇒ `allow` ⇒ Write erfolgt (Structured + tier3) |
| `test_default_gdi_off_unchanged` | Default (GDI aus) ⇒ `gdi_drift=None` ⇒ Write erfolgt, **kein** GDI-Schritt |
| `test_observe_gdi_grenze_tau_genau_allow` | Grenze `GDI ≤ τ` flaggt nicht (`>` strikt, Gl. 15) |

**Akzeptanz (ausgeführt):**

- `.venv/bin/python -m pytest tests/test_d2_gdi_prewrite.py -q --no-cov`
  → **4 passed**.
- `.venv/bin/python -m pytest -m "not network and not live" -q --no-cov -p no:cacheprovider`
  → **733 passed, 27 deselected**.
- Coverage der geänderten Kern-Dateien → **100 %**:
  `lifecycle_runner.py` (175 Stmts / 52 Branches, 0 missed),
  `pipeline.py` (22 / 4, 0 missed),
  `write_gateway.py` (309 / 104, 0 missed).
- `ruff check` + `ruff format --check` (geänderte/neue Dateien) → sauber.

**Ehrlicher Hinweis (keine Erfindung):** Die Tests nutzen einen **Stub-`embed_fn`**
(konstanter Vektor ⇒ Δ_sem = 0) und die injizierte Kalibrierung
`{sem 0.0, lex 0.85, struct 0.0, dist 0.15, τ 0.24}` (identisch zu
`tests/test_gdi_betrieb.py`); das echte Embedding (Endpoint, Guardrail 7) wird
im Unit-Test **nicht** aufgerufen. Es wird **nichts** neu kalibriert und **keine**
Zahl erfunden. Der Gesamt-Coverage-Wert des gefilterten Laufs (< 100 %) ist
**vorbestehend**: `reflective_agent.py` (LLM-Zweig) und `zsre_corpus.py`
(`datasets.load_dataset`) werden nur von `network`/`live`-Tests erreicht, die
hier ausgeschlossen sind; die drei Ziel-Dateien sind 100 %.

## 6. §9-Gate

**`approved`** – §9-Freigabe Batnini + Taoufik. Die Änderung ist eine
**Interface-Änderung** von Bestandsmodulen (`route_and_store` +
`write_gateway.store`: neuer Parameter `gdi_drift`) – kenntlich gemacht. Alle
neuen Parameter haben **rückwärtskompatible Defaults** (`None`) ⇒
Default-Verhalten unverändert. Keine neue Quelle (SAHOO + Mechanik bereits in
§9.1c verankert), kein `self_update` an Originaldateien. Test/`data/` ⇒
**kein** `versions/vN`. **Kein** `git add/commit/push` (Guardrail 6).
