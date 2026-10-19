# 121 — Environment-Fix: repo-eigenes `.venv` (Python 3.11, `mcp==1.30.0` gepinnt)

**Datum:** 2026-10-17
**Regeln:** AGENTS.md Guardrail 6 (Z.103: kein git add/commit/push), Guardrail 7 (Z.105-107: echte
Verifikation, kein Fake/Skip-Ersatz), Guardrail 3 (Z.99: Provenienz-Pflicht), §9.1d (Z.176-180).
**Trennung:** Abschnitte *gemessen* / *geschätzt* / *offen*; jede Behauptung mit Befehl + Rohtext.

---

## 1. Warum (Problemstellung)

System-Python `/usr/bin/python` = **3.9.25**; `tests/test_shacl_inferenz.py` (und damit die SHACL-
Inferenz) kann dort wegen fehlendem `pyshacl` nicht laufen; das offizielle `mcp`-SDK erfordert
Python >= 3.10 (`requirements-dev.txt:13-14`). Folge: der gefilterte Suite-Lauf ist unter dem
Default-Interpreter rot, obwohl der Code intakt ist.

---

## 2. PHASE 1 — Verifikation (read-only; nur `pip index`/`--dry-run`, nichts installiert)

### (a) Reproduktion der roten Baseline — BESTÄTIGT (gemessen)

```text
$ python -m pytest tests/ --ignore=tests/test_shacl_inferenz.py \
    -m "not network and not live" -o addopts= -q -p no:cacheprovider
...
12 failed, 793 passed, 4 skipped, 27 deselected, 2 errors in 19.82s   # EXIT=1
```

Namentlich (short test summary, Rohtext):

```text
FAILED tests/test_connector_binding.py::test_validate_connector_shacl - Modul...
FAILED tests/test_connector_binding.py::test_bind_pipeline_mit_mcp_record - M...
FAILED tests/test_connector_binding.py::test_bind_unbekannter_prozess - M...
FAILED tests/test_connector_binding.py::test_bind_all_17 - ModuleNotFoundErro...
FAILED tests/test_connector_binding.py::test_bind_liefert_integrations_modus
FAILED tests/test_mcp_live_binding.py::test_call_tool_live_eigener_server - a...
FAILED tests/test_mcp_live_binding.py::test_catalog_server_live - ModuleNotFo...
FAILED tests/test_mcp_live_binding.py::test_catalog_server_probe_fehler - Mod...
FAILED tests/test_mcp_live_binding.py::test_call_tool_live_rejected_write - K...
FAILED tests/test_skill_interpreter.py::test_agent_memory_write_in_process_mcp
FAILED tests/test_skill_interpreter.py::test_n5_validierungsfehler_kein_fallback
FAILED tests/test_skill_interpreter.py::test_k7_domain_reject_kein_fallback
ERROR tests/test_mcp_live_binding.py::test_call_tool_live_streamable_http - M...
ERROR tests/test_mcp_live_binding.py::test_catalog_server_streamable_http - M...
```

### (b) Einzige Ursache = fehlende Pakete — BESTÄTIGT (gemessen), mit 2 Präzisierungen

* Import-Stellen der Module-Errors: `data/memory/shacl_inferenz.py:21`,
  `data/memory/mcp_memory_server.py:307`, `scripts/mcp_probe.py:16`.
* `rdflib` fehlt NICHT: `python -c "import rdflib; print(rdflib.__version__)"` → `rdflib 7.6.0`;
  `import pyshacl` → `ModuleNotFoundError: No module named 'pyshacl'`; `import mcp` → gleicher Error.
* 5 der 12 sind selbst Assertions (2× `test_mcp_live_binding` :43/:92, 3× `test_skill_interpreter`
  :123/:173/:224 = `'local-fallback' == 'mcp'`), kausal mcp-bedingt (§11-Fallback ohne SDK):
  Kreuzcheck unter `/tmp/kvenv` (beide Pakete vorhanden):

```text
$ /tmp/kvenv/bin/python -m pytest tests/test_connector_binding.py tests/test_mcp_live_binding.py \
    tests/test_skill_interpreter.py -m "not network and not live" -o addopts= -q
56 passed in 4.27s   # EXIT=0
```

### (c) requirements-dev.txt — BESTÄTIGT (Rohtext, `grep -n`)

```text
13:# MCP-SDK (offiziell: PyPI `mcp`, requires-python >=3.10; Marker -> 3.9 ueberspringt)
14:mcp[cli]; python_version >= "3.10"
16:rdflib==7.6.0
17:pyshacl==0.40.1
```

Zusatz (pip-Märkte, read-only): `python -m pip index versions mcp` (3.9) →
`ERROR: No matching distribution found for mcp`; `python3.11 -m pip install --dry-run "mcp[cli]"` →
`Would install ... mcp-2.3.0 ...` (EXIT=0, nichts installiert) ⇒ **unpinned = 2.3.0**.

### (d) Interpreter / venv / git — BESTÄTIGT bei Versionen, Präzisierung bei „modified"

```text
$ python --version          → Python 3.9.25
$ python3.11 --version      → Python 3.11.13
$ ls -d .venv               → (vor Phase 3: kein .venv)
$ grep -n venv .gitignore   → 4:.venv/
$ git rev-parse --short HEAD → 4bd63cb
$ git status --porcelain | wc -l → 18   # 16 M + 2 ?? (FIX 5/Phase A, bewusst uncommitted)
```

### (e) `/tmp/kvenv` — BESTÄTIGT (gemessen, Volllauf grün)

```text
$ cat /tmp/kvenv/pyvenv.cfg
home = /usr/bin
include-system-site-packages = false
version = 3.11.13
executable = /usr/bin/python3.11
command = /usr/bin/python3.11 -m venv /tmp/kvenv
$ /tmp/kvenv/bin/python -m pip list --format=freeze | grep -E "^(mcp|pyshacl|rdflib|pytest|...)=="
mcp==1.30.0  pyshacl==0.40.1  rdflib==7.6.0  pytest==8.4.2  pytest-cov==7.1.0
pydantic==2.11.4  numpy==2.0.2  scipy==1.13.1  openai==2.36.0  datasets==4.5.0
ruff==0.16.10  json_repair==0.44.1  pymarkdownlnt==0.9.41  uvicorn==0.54.0  typer==0.27.3
$ /tmp/kvenv/bin/python -m pytest tests/ --ignore=tests/test_shacl_inferenz.py \
    -m "not network and not live" -o addopts= -q -p no:cacheprovider
810 passed, 1 skipped, 27 deselected in 23.13s   # EXIT=0
```

### (f) pytest.ini + conftest — BESTÄTIGT (Rohtext)

```text
$ sed -n '1,20p' pytest.ini
addopts =
    -ra
    --strict-markers
    --cov-branch
    --cov=data/memory
    --cov=skills
    --cov=ergebnisse/rekursion/solver
    --cov-report=term-missing
    # Mindest-Score: 100 % Gesamt-Coverage (Line + Branch, siehe .coveragerc)
    --cov-fail-under=100
markers =
    network: braucht das echte LLM-Endpoint (nicht fuer `make test`)
    live: braucht echte Quellen/Endpoint (Guardrail 7)
```

`tests/conftest.py:20-29` liest `OPENAI_API_KEY` aus `~/.config/opencode/opencode.json`
(`provider → nvidia-llama-nemotron → options → apiKey`); Messung (nur Boolean, kein Wert ausgegeben):
`conftest config exists: True | apiKey gesetzt (Boolean): True`.

---

## 3. PHASE 2 — Herkunft `/tmp/kvenv` + Entscheidung

**Herkunft (gemessen):** erzeugt am **2026-10-16 10:34:22** mit
`/usr/bin/python3.11 -m venv /tmp/kvenv` (Befehl steht in `pyvenv.cfg`; Install-Zeiten der
dist-Infos 10:34-10:35). Verwendet und referenziert in früheren Iterationen:
`ergebnisse/rekursion/117-…md:21`, `119-write-back-guard-fix-test.md:5`
(„Befehl (Python 3.11-venv, `/tmp/kvenv`)"), `120-fix5-poisoning-default.md:21/173`.
**Status: flüchtig** (`/tmp` → nach Reboot/`tmp`-Aufräumen weg). **Nicht gelöscht** (blieb während
dieser Runde unangetastet: `ls -d /tmp/kvenv` + `--version` → `Python 3.11.13`).

**Entscheidung (befohlen, umgesetzt):** deterministische repo-eigene Umgebung
`.venv` (Python 3.11.13) gebaut aus `-r requirements-dev.txt` **plus explizitem Pin**
`mcp[cli]==1.30.0` — bewusst NICHT das unpinned `mcp[cli]` allein, weil der Dry-Run sonst
`mcp-2.3.0` zieht (API-Bruchrisiko, Abschnitt 2c). **Kein §9-Human-Gate nötig:** reine
Umgebungsänderung, keine Code-/Interface-Änderung (§9 Z.120 greift auf Interface-Änderungen);
Anweisung lag explizit im Auftrag. **Kein sudo** (venv user-lokal).

---

## 4. PHASE 3 — Umsetzung + Tests (gemessen)

### Umbau

```text
$ python3.11 -m venv .venv && .venv/bin/python --version → Python 3.11.13
$ .venv/bin/python -m pip install -r requirements-dev.txt "mcp[cli]==1.30.0"
Successfully installed ... mcp-1.30.0 ... pyshacl-0.40.1 rdflib-7.6.0 pydantic-2.11.4
pytest-8.4.2 pytest-cov-7.1.0 ruff-0.16.10 uvicorn-0.54.0 typer-0.27.3 ...   # INSTALL_EXIT=0
$ .venv/bin/python -m pip list --format=freeze | grep -E "^(mcp|pyshacl|rdflib|pytest|pydantic)=="
mcp==1.30.0  pyshacl==0.40.1  rdflib==7.6.0  pytest==8.4.2  pydantic==2.11.4
```

(`Makefile:4` bevorzugt automatisch `.venv/bin/python`, sobald vorhanden → `make test` nutzt es.)

### (i) Gefilterter Lauf — erwartet 810/1/0 rot: ERFÜLLT

```text
$ .venv/bin/python -m pytest tests/ --ignore=tests/test_shacl_inferenz.py \
    -m "not network and not live" -o addopts= -q -p no:cacheprovider -rs
810 passed, 1 skipped, 27 deselected in 23.99s     # RUN_I_EXIT=0
SKIPPED [1] tests/test_lifecycle_discard.py:155: kein Konsolidierungs-State vorhanden
```

### (ii) Echter Coverage-Lauf OHNE `-o addopts=` (Gate `--cov-fail-under=100`): 100 % NICHT erreicht

```text
$ .venv/bin/python -m pytest tests/ --ignore=tests/test_shacl_inferenz.py \
    -m "not network and not live" -q -p no:cacheprovider
810 passed, 1 skipped, 27 deselected in 29.96s
FAIL Required test coverage of 100% not reached. Total coverage: 96.76%   # COV_EXIT=1
```

Lücken (aus dem `coverage report` dieses Laufs, Stmts/verpasst):

```text
data/memory/evaluator_version.py    450  50  88%
data/memory/gaama_extract.py        103  30  76%
data/memory/ingestion_hook.py       280   1  99%
data/memory/mcp_live_binding.py     110   6  95%
data/memory/reflective_agent.py     266   2  99%
data/memory/shacl_inferenz.py        34  25  18%   # -> war --ignore (seine Tests nicht gelaufen)
data/memory/write_gateway.py        309   2  99%   # Zeilen 504, 506
data/memory/zsre_corpus.py           56  23  62%
TOTAL                              4369 139  97%  (Total coverage: 96.76 %)
```

**Varianten, um die100 %-Frage sauber zu beantworten:**

```text
(ii-b) ohne --ignore, sonst gleich:
$ .venv/bin/python -m pytest tests/ -m "not network and not live" -q -p no:cacheprovider
817 passed, 1 skipped, 27 deselected in 29.97s
FAIL Required test coverage of 100% not reached. Total coverage: 97.49%   # EXIT=1

(ii-c) kanonischer Volllauf inkl. network/live (echter Key):
$ timeout 600 make test
... tests/test_fwr.py ..
make: *** [Makefile:9 test] Terminated            # von timeout getötet (EXIT 124 des make-Kommandos)
```

Einzeltest-Isolierung (gemessen, `timeout 150`):

```text
$ timeout 150 .venv/bin/python -m pytest tests/test_fwr.py -v -p no:cacheprovider
tests/test_fwr.py::test_non_write_real PASSED
tests/test_fwr.py::test_write_new_real FWR_EXIT=124    # hing >150 s, wurde getötet
```

Ursache des Hängers (Datei-/Code-Beleg): `tests/test_fwr.py:10` nutzt `from _live import call`;
`tests/_live.py:27` → `def call(fn, *args, attempts: int = 18, base_delay: float = 4.0,
max_delay: float = 20.0, …)` — bis zu 18 Versuche mit Backoff bis 20 s pro echtem Endpoint-Call
(kein Fake, Guardrail 7 erfüllt), dokumentiertes Hänger-Risiko aus Rek 119 realisiert.
**Folge: der100 %-Gesamt-Coverage-Lauf ist mit diesem Endpoint-Lauf NICHT abgeschlossen worden —
Wert offen (nicht 100 %, nicht endgültig <100 %).**

**Netz/Key:** nur echte Calls (kein Stub/Skip als Ersatz); Key-Messung Boolean `True`
(Abschnitt 2f); Hänger-Begrenzung jeweils per `timeout` protokolliert (600 s `make test`,
150 s Einzeltest).

---

## 5. Geändert / nicht geändert

**Geändert (Umgebung, untracked):** `.venv/` neu gebaut (Python 3.11.13, `mcp==1.30.0` gepinnt);
Nebenprodukte `.coverage`, `.pytest_cache/` — alle drei in `.gitignore` (Z.4, 14, 15).
**Nachtrag (Auftrag Nutzer 2026-10-17):** `AGENTS.md` Guardrail 8 in 2 Zeilen ergänzt
(Z.108-109: alle Läufe über `.venv`, `make test`/`pytest` mit `.venv/bin/python`) — Änderung am
Gesetzes-File protokolliert hier (§9.1b-Versionierung in Git erfolgt nicht, Guardrail 6).
**Nicht geändert:** keine Quell-/Testdatei editiert; **kein git-Befehl** ausgeführt —
`git rev-parse --short HEAD` → `4bd63cb`, `git status --porcelain | wc -l` → `18` (identisch zu
Phase 1: 16 M + 2 ??, unverändert aus FIX 5/Phase A).
**Nicht angefasst:** `/tmp/kvenv` (bewusst, siehe Phase 2).

---

## 6. Ehrliche Trennung

**Gemessen:**
- Baseline 3.9: `12 failed, 793 passed, 4 skipped, 27 deselected, 2 errors`, EXIT=1, namentlich belegt.
- Ursache Pakete (pyshacl fehlt, mcp fehlt, rdflib 7.6. da), Kreuzcheck kvenv `56 passed`.
- kvenv-Herkunft (2026-10-16 10:34, `python3.11 -m venv /tmp/kvenv`) + Volllauf `810/1/27` EXIT=0.
- `.venv` gebaut, Pins `mcp==1.30.0`/`pyshacl==0.40.1`/`rdflib==7.6.0` gesetzt, INSTALL_EXIT=0.
- Lauf (i): `810 passed, 1 skipped, 27 deselected`, EXIT=0 (Erwartung erfüllt).
- Coverage (ii): `96.76 %`, EXIT=1; (ii-b): `97.49 %`, EXIT=1; Lückenliste oben.
- Hänger: `test_fwr.py::test_write_new_real` >150 s; `make test` bei 600 s getötet; Beleg `_live.py:27`.
- Key vorhanden (Boolean), git unverändert (`4bd63cb`, 18 Einträge).

**Geschätzt:**
- Restlücke zu 100 % liegt v. a. in Live-/Netz-Pfaden (`mcp_live_binding`, `evaluator_version`,
  `gaama_extract`) — nur indirekt abgeleitet aus den Lückenlisten, NICHT per erfolgreichem
  Live-Volllauf bestätigt.
- Ein grüner kanonischer `make test`-Lauf ist plausibel, wenn der Endpoint stabil antwortet
  (Retry-Puffer `18×` ist groß) — nicht belegt.

**Offen:**
1. `--cov-fail-under=100` mit Volllumfang (inkl. network/live): **nicht abgeschlossen** — braucht
   wiederholten Lauf bei stabilen Endpoint; Zwischenwerte 96.76 %/97.49 % nur für gefilterte Läufe.
2. `write_gateway.py:504,506` (99 %) und `zsre_corpus.py` (62 %) sind auch ohne Live-Tests ungedeckt.
3. `requirements-dev.txt:14` bleibt **ungepinnt** (`mcp[cli]`); der Pin galt nur für diesen Install-
   Aufruf. Empfehlung (nicht umgesetzt, nicht befohlen): `mcp[cli]==1.30.0` in die Datei schreiben.
4. Hänger-`test_write_new_real` — Endpunkt-Verhalten/Backoff-Interaktion, nicht abschließend analysiert.
