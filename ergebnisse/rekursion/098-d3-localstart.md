# Rekursion 098: Lokaler Live-Start + Erfolgs-Exit (D3, Audit d25486c)

> Datum: 2026-10-09 · Phasen: Observe → Compare → Revise. Ziel `g` (§2/§9.1):
> alle LLM-Phasen eines **lokalen** Laufs nutzen ein **vorhandenes** Modell, und der
> Driver darf einen **erfolglosen** Lauf nicht still mit **Exit 0** beenden.
> Quellen (**Belegt**, in `AGENTS.md` referenziert ⇒ **keine neue Quelle**):
> §7 (echte Verifikation, kein Fake), §11 (lokale Memory als Basis),
> §10.2 (`FWR_SMALL_MODEL`/`FWR_LARGE_MODEL` als lokale Router-Modelle),
> §6 (World-State-Oracle). Status: **`approved`** (§9-Freigabe Batnini + Taoufik) –
> **Interface-Änderung** (neue CLI `--require-success`), kenntlich gemacht.
> Kein `self_update` an `AGENTS.md`/`tier1-base`, kein `git`.

## 1. Befund (D3, P2 aus Audit d25486c)

- **Soll (§7/§11):** ein lokaler Live-Lauf muss **alle** LLM-Phasen (Router,
  Reflexion, Oracle) gegen das **lokale** Modell fahren; ein Lauf **ohne** Beleg
  darf nicht als Erfolg (Exit 0) durchgehen.
- **Ist (vorher):**
  1. Der dokumentierte lokale Start (Rekursion 095) setzte nur
     `FWR_SMALL_MODEL`/`FWR_LARGE_MODEL`, **nicht** `HELA_MODEL`. Reflexion
     (`data/memory/reflective_agent.py:106`, `:326`) und Oracle (`_ask`) lesen
     `HELA_MODEL` – dessen Default ist `nvidia/nemotron-3-ultra-550b-a55b`
     (`scripts/live_run.py:64`). Gegen den **lokalen** Endpoint
     (`http://127.0.0.1:11434/v1`) ⇒ **404** für Reflexion/Oracle.
  2. `scripts/live_run.py` beendete **jeden** Lauf nach dem Schreiben des JSON mit
     `return 0` (`main`), auch wenn **kein** Write und **kein** positives Oracle
     vorlag ⇒ stiller „Erfolg" trotz wirkungslosem Lauf.

## 2. Ist → Soll (Fix)

| Ort | Vorher | Nachher |
|---|---|---|
| `scripts/live_run.py` Start (nach `_resolve_endpoint`) | `HELA_MODEL` blieb ungesetzt | `_apply_hela_model_default()`: `HELA_MODEL` ← `FWR_LARGE_MODEL` → `FWR_SMALL_MODEL` → `DEFAULT_MODEL`, **nur** per `setdefault` (vorhandener Wert bleibt) |
| `_ask` (Oracle) | `model or REFLECTION_MODEL` (Import-Schnappschuss) | `model or os.environ.get("HELA_MODEL") or REFLECTION_MODEL` (Laufzeit-ENV) |
| CLI | nur `--tasks/--out/--seed/--approver` | + `--require-success` (Default **aus**): ohne erfolgreichen Write **und** ohne positives Oracle ⇒ **Exit 1** |
| `payload["model"]["reflection"]` | `REFLECTION_MODEL` | `os.environ.get("HELA_MODEL") or REFLECTION_MODEL` (effektiv genutztes Modell) |
| Doku (`--help`/Docstring) | ENV nicht dokumentiert | `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `FWR_SMALL_MODEL`, `FWR_LARGE_MODEL`, `HELA_MODEL` + `--require-success` |

**Erfolg (`_has_success`)** = erfolgreicher Write **oder** positives Oracle:
- Write = einer der beiden Runner meldet `ok=True` **und** `action` ∈
  {`write-new`, `write-update`} (§10.7);
- positives Oracle = `Compare.observed=True` (§6, externes Signal).

**Default unverändert:** ohne `--require-success` ist `main` exakt wie vorher
(Exit 0); ohne FWR-Modelle fällt `HELA_MODEL` auf `DEFAULT_MODEL` (altes Verhalten).

## 3. Umsetzung (Interface-Änderung §9 approved)

- `scripts/live_run.py`
  - `DEFAULT_MODEL`-Konstante; `REFLECTION_MODEL = os.environ.get("HELA_MODEL", DEFAULT_MODEL)`.
  - neu `_apply_hela_model_default(environ=None)` (testbar, `setdefault`-Semantik).
  - `_ask`: Modell zur Laufzeit aus ENV.
  - neu `_has_success(run)` + `_WRITE_ACTIONS`.
  - `main`: `_apply_hela_model_default()` nach `_resolve_endpoint`; neues
    `--require-success`; nach dem JSON-Write Exit-1-Prüfung mit klarer
    `FEHLER:`-Meldung auf `stderr`.
  - Docstring/`--help` dokumentieren die nötigen ENV-Flags.
- **Nicht** geändert: `AGENTS.md`, `data/memory/tier1-base/`, `data/`-Module
  (nur `scripts/` + Tests + Doku). Test/`data/` ⇒ **kein** `versions/vN`.

## 4. Diff (erwartet; `git status --short`/`--stat` siehe unten)

```
 scripts/live_run.py                          | geändert (D3: HELA-Default + --require-success)
 tests/test_d3_localstart.py                  | neu  (12 Tests)
 ergebnisse/rekursion/095-live-lokal.md       | korrigiert (HELA_MODEL=qwen-local + Hinweis)
 ergebnisse/rekursion/098-d3-localstart.md    | neu  (diese Datei)
 ergebnisse/rekursion/README.md               | +1   (Index-Zeile 098)
```

- `AGENTS.md` und `data/memory/tier1-base/` **nicht** geändert (Guardrail 6,
  §9.1b). Keine neue Quelle.

## 5. Compare / Tests (offline, echtes Test-Signal)

Neues Repro (`tests/test_d3_localstart.py`, offline; Guardrail 7 – **kein**
Netz/Endpoint, gestubbte `_resolve_endpoint`/`_load_tasks`/`_run_task`):

| Test | Aussage |
|---|---|
| `test_hela_default_aus_fwr_large` | fehlendes `HELA_MODEL` ← `FWR_LARGE_MODEL` (lokal) |
| `test_hela_default_aus_fwr_small` | ohne Large ← `FWR_SMALL_MODEL` |
| `test_hela_default_fallback_default_model` | ohne FWR-Modelle ← `DEFAULT_MODEL` |
| `test_hela_vorhandener_wert_bleibt` | vorhandenes `HELA_MODEL` wird **nicht** überschrieben |
| `test_has_success_bei_write` | `ok=True` + `write-*` ⇒ Erfolg |
| `test_has_success_bei_positivem_oracle` | `observed=True` ⇒ Erfolg |
| `test_has_success_ohne_write_und_ohne_oracle` | kein Write, kein Oracle ⇒ kein Erfolg |
| `test_require_success_ohne_erfolg_exit1` | `--require-success`, 0 Erfolge ⇒ **Exit 1** |
| `test_require_success_mit_write_exit0` | `--require-success`, Write ⇒ **Exit 0** |
| `test_require_success_mit_positivem_oracle_exit0` | `--require-success`, Oracle ⇒ **Exit 0** |
| `test_ohne_flag_exit0` | ohne Flag ⇒ **Exit 0** (altes Verhalten) |
| `test_main_setzt_hela_model` | Verdrahtung: `main` setzt den Default real |

**Akzeptanz (ausgeführt):**

- `.venv/bin/python -m pytest tests/test_d3_localstart.py -q --no-cov`
  → **12 passed**.
- `.venv/bin/python -m pytest -m "not network and not live" -q --no-cov -p no:cacheprovider`
  → **752 passed, 27 deselected** (keine Regression).
- `ruff check` + `ruff format --check` (`scripts/live_run.py`,
  `tests/test_d3_localstart.py`, `tests/test_freigabe_pfad.py`) → sauber.

**Ehrlicher Hinweis (keine Erfindung):** Die Tests sind **offline** (Guardrail 7):
der echte lokale Live-Lauf (Ollama + GGUF) wird hier **nicht** aufgerufen; die
Tests belegen die **Verdrahtung** (ENV-Default + Exit-Semantik), nicht die
Modellqualität. Es wird **nichts** neu kalibriert und **keine** Zahl erfunden.
`tests/test_freigabe_pfad.py` wurde **nicht** geändert (keine Anpassung nötig).

## 6. §9-Gate

**`approved`** – §9-Freigabe Batnini + Taoufik. Die Änderung enthält eine
**Interface-Änderung** (neue CLI `--require-success`) – kenntlich gemacht. Die
neue Option hat Default **aus** ⇒ Verhalten ohne Flag unverändert; der
`HELA_MODEL`-Default nutzt `setdefault` ⇒ vorhandener Wert unverändert. Keine neue
Quelle (§6/§7/§10.2/§11 bereits verankert), kein `self_update` an
Originaldateien, kein `git add/commit/push` (Guardrail 6).
