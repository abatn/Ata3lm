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
  --approver Batnini --approver Taoufik --workdir /kaggle/working \
  --llm-base-url http://127.0.0.1:11434/v1 --llm-model qwen2.5:1.5b
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

## 8. Nachtrag — lokales Ollama statt Secrets (2026-10-11)

**Anlass:** Der Driver war an einen externen LLM-Endpoint + `OPENAI_API_KEY` gebunden
(flaky, Secret-Handling im Notebook). Der Betreiber setzt stattdessen **lokales
Ollama auf Kaggle** ein; Secret-Loading im Skript ist **unnötig** und wurde entfernt.

**Änderung (nur `kaggle/write_back_cycle.py`, additiv):**
- **Entfernt:** `_SECRET_ENV`, `_load_kaggle_secrets()` (Secret-Handling) inkl. Aufruf.
- **Neu:** `_configure_llm_env()` (setzt `OPENAI_BASE_URL`=`http://127.0.0.1:11434/v1`,
  `OPENAI_API_KEY`=`ollama`, `FWR_SMALL_MODEL`/`FWR_LARGE_MODEL`/`HELA_MODEL`=`--llm-model`;
  vorhandene ENV hat Vorrang) · `_llm_endpoint_ok()` (realer `GET /v1/models`,
  fail-closed) · CLI `--llm-base-url`/`--llm-model` · Ergebnis-Felder `llm_base_url`/`llm_model`.
- **Korrigiert:** Key-Check → **echter Endpoint-Check**; `_ThetaProbe` nutzt
  `dtype=` (transformers ≥ 4.56/5.x, PR #39782) mit `torch_dtype`-Fallback.

**Verifikation (lokal, echt):** `ruff`/`format` grün · `ast.parse` ok · `--help` zeigt
neue Flags · ENV-Setzung korrekt · Endpoint-Check **real gegen lokales Ollama** =
`HTTP 200` · unreachbarer Port → `False` · **33 passed** (`test_slow_consolidation`,
`test_kaggle_train_cli`).

**Status:** `approved` (Batnini + Taoufik) — Artefakt bleibt **`unverifiziert`**: der
echte **Kaggle-Lauf (GPU)** steht weiter aus (kein `torch`/`peft` lokal). Kaggle-Zellen
(Ollama installieren/starten/pullen) dokumentiert in `kaggle/README.md`.

## 9. Nachtrag — Kaggle-Lauf-Befund: inkompatibles `torchao` (2026-10-11)

**Beobachtung (echter Kaggle-Lauf, Ausgabe):** Der Lauf kam bis zur **Θ′-Probe** und
brach in `peft` ab:

```
peft/peft_model.py:611 → tuners_utils.py:917 → lora/model.py:281/430
→ lora/torchao.py:160 dispatch_torchao → import_utils.py:147 is_torchao_available
ImportError: Found an incompatible version of torchao. Found version 0.10.0,
but only versions above 0.16.0 are supported
```

**Ursache (Belegt, Quelltext gelesen):** peft v0.20.0
`src/peft/import_utils.py::is_torchao_available` **raise**t `ImportError`, wenn
`torchao < 0.16.0` installiert ist (statt `False`). Die LoRA-Injektion erreicht
`dispatch_torchao` (`lora/model.py:413-430`) nur, wenn kein früherer Dispatcher
greift — bei **4-bit-bnb** (Training) greift `dispatch_bnb_4bit` zuerst, bei der
**nicht**-4-bit Θ′-Probe erreicht sie `dispatch_torchao` ⇒ Abbruch. Kaggle liefert
`torchao 0.10.0`.

**Fix (Quelle: ebd.):** `pip uninstall -y torchao` (⇒ `find_spec` None ⇒
`is_torchao_available` False ⇒ `dispatch_torchao` liefert `None`) **oder**
`pip install -U "torchao>=0.16.0"`.

**Artefakt-Änderung (nur `kaggle/write_back_cycle.py`, additiv):**
`_torchao_incompatible()` erkennt `torchao < 0.16.0`; `main()` bricht damit
**fail-closed** mit klarer Fix-Anweisung ab (statt kryptischem Traceback). Kaggle-Zelle
in `kaggle/README.md` ergänzt. **Kein** Eingriff in `data/memory/*` oder peft.

**Verifikation (lokal):** `ruff`/`format` grün · `ast`/Import ok · `--help` ok ·
`_torchao_incompatible()` = `None` (torchao lokal nicht installiert, unkritisch).

**Frage an den Betreiber (§9-Gate, Interface):** Reicht die **Umgebungs-Zelle**
(`pip uninstall -y torchao`) — oder soll der Driver den inkompatiblen Baustein
**automatisch** entfernen (zusätzliche Mutation)? Vorschlag: **Zelle** (explizit,
nachvollziehbar, keine Laufzeit-Systemmutation).
