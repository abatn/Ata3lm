# Rekursion 087: Live-Run-Driver für 8 Stufen + 5 Phasen

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare → Revise.
> Ziel `g`: ein **echter** Endpoint-Lauf, der je Aufgabe sowohl den
> 8-Stufen-Zyklus (`lifecycle_runner.run_cycle`) als auch die 5-Phasen-Rekursion
> (`recursion_runner.run_recursion`) über **dieselbe** persistente State-Datei
> fährt und die Spur (Stufen/Phasen, `gate`, `ok`, `observed`, Ergebnisdaten)
> nach `ergebnisse/live-run.json` schreibt.
> Status: **pending** – Unit-/Verdrahtungstests grün; der echte Lauf und die
> §9-Freigabe liegen beim Auftraggeber (kein Fake, Guardrail 7).

## 1. Soll (Gesetz + Quellen)

- 8 Stufen: `AGENTS.md` §3 · `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`.
- 5 Phasen: `knowledge/lifecycle/rekursion/index.md` §2 (Konstrukt → Akt →
  Observe → Compare → Revise).
- Compare nur mit **externem** Signal: `AGENTS.md` §6 · `world_state_oracle`
  (arXiv:2607.25152, „out-of-band evaluation is a structural requirement").
- FWR-Klassifikator: `AGENTS.md` §10 · `data/memory/fast_write_router.py`
  (arXiv:2608.22215) via `classify(question, fact, correct)`.
- Aufgabenkorpus: ZsRE `community-datasets/qa_zre` via `zsre_corpus`
  (neue Quelle ⇒ §9 Human-Gate `ask`, in `zsre_corpus.py` bereits kenntlich).

## 2. Ist (neu)

| Ort | Inhalt |
|---|---|
| `scripts/live_run.py` | CLI `--tasks N` · `--out` · `--seed`; `_resolve_endpoint` (ENV **oder** `~/.config/opencode/opencode.json`, Provider `nvidia-llama-nemotron`), `_load_tasks`/`_record_to_task`/`_load_zsre_records`, `_summarize_cycle`, `_summarize_recursion`, `_run_task`, `main`. |
| `tests/test_live_run.py` | 11 Offline-Tests (Stubs/Injektion, kein Netz). |

**Ablauf je Aufgabe:** `run_cycle(...)` (8 Stufen, `classify_fn=fast_write_router.classify`,
`structured_dir`/`tier3_dir` im tmp-Ordner) schreibt den Runner-State; unmittelbar
danach `run_recursion(...)` mit **demselben** `state_path` (K1-Restart über die
Datei; ein eigener Prozess kann denselben Pfad nutzen). Der 5-Phasen-Runner
erhält ein **echtes** `world_state_probe` (§6): eine unabhängige Out-of-Band-LLM-
Abfrage des gespeicherten Fakts gegen das ZsRE-Gold — der Selbstreport ist nur
Annotation.

**Layout:** `structured/` + `tier3/` je Aufgabe unter einem `TemporaryDirectory`;
`LIFECYCLE_DRIFT_REFERENCE` wird auf tmp gesetzt ⇒ kein Schreiben in
`data/memory/tier2-index/`. Ausgabe: `{tasks:[{question, fact, correct, cycle, recursion}], model, source, n, seed}`.

**Kein Fake (§6/Guardrail 7):** fehlt der Key/Endpoint, bricht `main()` mit
klarem `RuntimeError` ab, ohne eine Datei zu schreiben. Es werden nur echte
Endpoint-Antworten und echte ZsRE-Zeilen verwendet.

## 3. Diff

```
scripts/live_run.py          | neu
tests/test_live_run.py       | neu
ergebnisse/rekursion/087-live-run-driver.md | neu
ergebnisse/rekursion/README.md | +1 Index-Zeile
```

`AGENTS.md` und `data/memory/tier1-base/` wurden **nicht** geändert.

## 4. Compare / Tests (offline; kein Netz)

**Akzeptanz (ausgeführt):**

- `.venv/bin/python -m pytest tests/test_live_run.py -q --no-cov` → **11 passed**.
- `.venv/bin/python -m ruff check scripts/live_run.py tests/test_live_run.py` → sauber.
- `.venv/bin/python -m ruff format --check ...` → „2 files already formatted".
- `.venv/bin/python scripts/live_run.py --help` → CLI ok; mit fehlendem Key
  (`HOME=/tmp/nonexistent`) → klarer Fehler „OPENAI_API_KEY/Endpoint fehlt …".

| Testblock | Aussage |
|---|---|
| `_summarize_cycle` | Stufen/`ok`/`action`/`gate`/`revised`/`DI` + `results` korrekt; leere Eingabe robust |
| `_summarize_recursion` | Phasen/`ok`/`gate`/`observed`/`score`/`compare_gate`/`revised`; ohne Revise `None` |
| `_record_to_task` | gültig ↔ leer/zu kurz/kein Record ⇒ `None` (nichts erfunden) |
| `_load_tasks` | injizierter Loader, Skip ungültiger Zeilen, `n`-Cap, Seed-Determinismus |
| `_resolve_endpoint` | ENV-Vorrang, Config-Fallback, fehlender Key ⇒ `RuntimeError` ohne Netz |
| `_run_task` | beide Runner real verdrahtet, LLM-Stufen gestubbt: Stufen-/Phasen-Namen, externes `observed=True`, NOOP-Matrix ⇒ `revised=False` |

**Nicht Teil dieses Tests (Guardrail 7):** der echte Endpoint-/ZsRE-Lauf wird vom
Auftraggeber gestartet (`python scripts/live_run.py --tasks N --seed S`).

## 5. §9-Gate

- **Kein Interface an Bestandsmodulen:** keine Signatur/Formatänderung an
  `lifecycle_runner`, `recursion_runner`, `fast_write_router`, … Es werden
  ausschließlich bestehende, öffentliche Aufrufe verwendet
  (`run_cycle`, `run_recursion`, `classify`, `write_gateway.default_mandate`).
- **Neue Dateien** (`scripts/live_run.py`, `tests/test_live_run.py`) – Skript/Test,
  kein `versions/vN` (`data/memory/` unberührt).
- **Neue Quelle:** nein – ZsRE ist bereits über `zsre_corpus` (§9 `ask`,
  `AGENTS.md` §10.3) eingebunden.
- **Human-Gate:** Status `pending`; der echte Lauf und die Freigabe erfolgen durch
  den Auftraggeber.
- **Kein** `git add/commit/push` (G6).
