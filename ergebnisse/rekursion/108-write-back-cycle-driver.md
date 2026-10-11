# Rekursion 108: V1 geschlossener Write-Back-Zyklus (Kaggle-Driver)

> Datum: 2026-10-11 · Phasen: Konstrukt → Akt → Observe → **Compare** → Revise
> (externes Signal: Kaggle-GPU-Lauf).
> Ziel `g` (§2/§10.3): den **echten** geschlossenen Zyklus
> **Sammeln → SFT-Dataset → Training → Probe → Flush** ausführbar machen.
> Quellen: `AGENTS.md` §10.3/§10.5/§9.3, arXiv:2608.22215 §3.4,
> `connectors/gaama.md` (Kairos, validation-gated).
> Status: **`approved`** (Batnini + Taoufik, 2026-10-11, §9.3) — die **Ausführung
> auf Kaggle (GPU)** steht aus ⇒ Artefakt bis dahin **`unverifiziert`**.

## 1. Anlass

Audit `e2e-699dda4` (D3): `slow_consolidation.write_back` war ein ehrlicher Stub
(`NotImplementedError`); die **SFT→Serving→Probe→Flush-Kette** fehlte.

## 2. Artefakt (neu)

`kaggle/write_back_cycle.py` (V1, Kaggle-GPU, **kein Fake**):
1. reale Fakten (`zsre_corpus.build_zsre_corpus`, split=validation),
2. **reale Writes** über `pipeline.route_and_store` (`fast_write_router.classify`,
   `write_gateway.default_mandate`), §9.3: nur mit **≥ 2 distinkten** `--approver`,
3. `collect_pending(...)`,
4. `train_fn` = **echtes** SFT (Subprocess `train_slow_consolidation.py` → `kaggle_output.json`),
5. `probe_fn` = **echte** Base-vor-Adapter-Generierung (N8), Teilstring-Prüfung,
6. `write_back(..., train_fn, probe_fn, tier3_dir, provenance_log, state_path)` →
   **Flush nur bei positivem Probe** (fail-closed), Ergebnis `write_back_cycle_result.json`.

## 3. Aufruf (Kaggle, GPU)

```bash
python kaggle/write_back_cycle.py --n 20 --gpu 0 \
  --approver Batnini --approver Taoufik --workdir /kaggle/working
```

## 4. Verifikation (lokal)

- `ast.parse` ok · `--help` ok · `ruff check .` + `format --check .` grün (117 Dateien).
- **Keine Interface-Änderung** an bestehenden Modulen (nur neue Datei); **kein Git**.

## 5. §9-Gate / Freigabe

- Neue Datei (additiv); §9.3 = **freigegeben** (Batnini + Taoufik, 2026-10-11).
- **Caveat (Audit):** die CLI-`--approver`-Namen **authentifizieren keine** natürlichen
  Personen; die Freigabe wird **vor** dem Kaggle-Start durch den Betreiber erklärt.

## 6. Ehrlicher Caveat / offen

- **GPU-Beweis fehlt** (lokal kein `torch`/`transformers`/`peft`): erst der Kaggle-Lauf
  zeigt `flushed/kept/loss`. Bis dahin gilt der Zyklus als **`unverifiziert`**.
- Bei Fehler: **Stopp + Rollback** (Working-Tree), Traceback mitbringen.

## 7. Quellen (belegt)

- arXiv:2608.22215 §3.4 (Write-Back: erfolgreich ⇒ Flush, sonst bleibt).
- `connectors/gaama.md` (Kairos, validation-gated: kein Write ohne positiven Probe).
- `AGENTS.md` §10.3/§9.3; `scripts/live_run.py` (reales Schreibmuster).
