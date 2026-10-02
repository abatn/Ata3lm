# CI-Setup: pytest für den gesamten Knowledge-Agenten

> Datum: 2026-10-01 · Aufträge: „minimales CI/pytest-Setup" → „der ci muss auf
> 100 % geprüft" → „für die gesamte knowledge-agent gebaut für alles".
> Lab-Prinzip §6: nur Behauptungen, die in der Doku stehen (URL-Tabelle unten,
> HTTP 200 am 2026-10-01 geprüft) bzw. lokal nachlauffähig sind.

## 1. Gelieferte Dateien

| Datei | Zweck |
|---|---|
| `tests/conftest.py` | `sys.path` (data/memory, shared/, tier3-working/, skills) + Netzwerk-Sperre |
| `tests/test_fwr.py` (12) | FWR-Kaskade + Gate, `_ask` (Fake-Client), MemRouter, `compare_router_10` |
| `tests/test_governance.py` (10) | Zwei-Personen-Flow (§9.3) + Gesetzestext §9/§9.1 |
| `tests/test_memory.py` (14) | 3 Tiers, v1–v4, PII/Poisoning/Bias-Guards, JSD/Drift |
| `tests/test_bi_temporal.py` (5) | valid time × transaction time, Supersede statt Löschen |
| `tests/test_shared_memory.py` (8) | ACL, Trust-Konflikt, Schema, Sync, Dump |
| `tests/test_lru_cache.py` (10) | LRU-/Value-Eviction, Adaptive Forgetting, Tier-2-Auslagerung |
| `tests/test_ingestion.py` (17) | Privacy/Secrets, Encoding-Gate, GLiNER-Pfade, Graph-Konflikte, async Enrichment, Lifecycle |
| `tests/test_reflective.py` (20) | HMM-Trägheit, Hub/Forgetting, Destillation, Dual-Path-Retrieval, Lyapunov |
| `tests/test_procedural_memory.py` (7) | Skill-Snapshots, Human-Gate-Update, Rollback |
| `tests/test_evaluator_version.py` (56) | Red-Queen: Evaluator-Versionierung, Ground-Truth-Anker, Selective Erasure |
| `tests/test_solvers.py` (20) | 9 historische Solver-Snapshots (Ist-Verhalten) |
| `pytest.ini` | Konfiguration + **Mindest-Score** (`--cov-fail-under=100`) + Marker |
| `.coveragerc` | Coverage-Konfiguration; nimmt **nur** den `__main__`-Guard aus |
| `Makefile` | `make test` → `python3 -m pytest` (+ `make clean`) |
| `pyproject.toml` | Ruff-Konfiguration (line-length 120, py39, select E/F/W/I) |
| `.pre-commit-config.yaml` | Ruff + Ruff-Format (Rev v0.16.10) |
| `.github/workflows/ci.yml` | CI: Job `lint` (Ruff) + Job `test` (pytest 3.9/3.12) |
| `requirements-dev.txt` | Gepinnte Dev-/CI-Abhängigkeiten (+ json-repair) |
| `tests/test_agents_law.py` (8) | AGENTS.md-Konformität: §1–§11, Guardrails, Provenienz, Versionierung, CI-Verdrahtung |
| `.gitignore` | `.pytest_cache/`, `.coverage`, `coverage.xml`, `htmlcov/` |

## 2. Zwei Scores – nicht verwechseln

| Score | Definition | Quelle | Umsetzung |
|---|---|---|---|
| **§9-Test-Score** | bestandene Tests / Gesamttests (≥95 allow, 70–94 ask, <70 deny) | `AGENTS.md` §9 | pytest Exit-Code ≠ 0 bei **jedem** fehlgeschlagenen Test; 189/189 = 100 % |
| **Mindest-Score (Coverage)** | abgedeckte Statements **und Branches** des gesamten Repo-Codes | pytest-cov `--cov-fail-under` + `--cov-branch` | `pytest.ini`: **100 %** (gemessen: 1651/1651 Statements, 360/360 Branches) |

**Gemessener Umfang (2026-10-01):** `data/memory/**` (9 Module: approval,
bi_temporal, bias_monitor, fast_write_router, ingestion_hook, reflective_agent,
shared/shared_memory, tier3-working/lru_cache, trust), `skills/procedural_memory.py`
und `ergebnisse/rekursion/solver/**` (10 Snapshots) = **1651 Statements / 360 Branches, 0 nicht abgedeckt**
(Line + Branch, `branch = True`).

**100 ist das Maximum:** `--cov-fail-under=101` wird abgelehnt
(`error: argument --cov-fail-under: … The maximum value is 100.`, `rc=4`).
Nachweis der 100-%-Schwelle daher über *weniger* Tests (nach `coverage erase`):

```text
$ python3 -m pytest -q --cov-branch -k "not reflective and not ingestion"
data/memory/ingestion_hook.py                         278    203     58      0    22%  ...
data/memory/reflective_agent.py                       242    193     48      0    17%  ...
TOTAL                                                1651    402    360      0    75%
FAIL Required test coverage of 100% not reached. Total coverage: 74.64%
150 passed, 39 deselected in 6.47s
rc=1 (erwartet 1)
```

**Warnung (selbst beobachtet):** Zwei Läufe parallel im selben Verzeichnis
verfälschen das Ergebnis, weil beide dieselbe `.coverage` schreiben – ein
solcher Parallel-Lauf zeigte fälschlich „100 %". Der Wert oben stammt aus
einem Lauf nach `coverage erase`; vor jedem Messen `python3 -m pytest` einzeln
ausführen.

## 3. Rohtext `make test` (2026-10-01, 100 %)

```text
python3 -m pytest
============================= test session starts ==============================
platform linux -- Python 3.9.25, pytest-8.4.2, pluggy-1.6.0
rootdir: /home/opc/knowledge-agent
configfile: pytest.ini
testpaths: tests
plugins: cov-7.1.0, asyncio-1.2.0, langsmith-0.4.37, anyio-4.12.1
asyncio: mode=strict, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 189 items

tests/test_agents_law.py ........                                        [  4%]
tests/test_bi_temporal.py .....                                          [  6%]
tests/test_evaluator_version.py ........................................ [ 28%]
................                                                         [ 36%]
tests/test_fwr.py ............                                           [ 42%]
tests/test_governance.py ..........                                      [ 48%]
tests/test_ingestion.py .................                                [ 57%]
tests/test_lru_cache.py ..........                                       [ 62%]
tests/test_memory.py ..............                                      [ 69%]
tests/test_procedural_memory.py .......                                  [ 73%]
tests/test_reflective.py ......................                          [ 85%]
tests/test_shared_memory.py ........                                     [ 89%]
tests/test_solvers.py ....................                               [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.9.25-final-0 ________________

Name                                                Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------------------
data/memory/approval.py                                41      0      8      0   100%
data/memory/bi_temporal.py                             51      0      8      0   100%
data/memory/bias_monitor.py                            84      0     18      0   100%
data/memory/evaluator_version.py                      450      0     94      0   100%
data/memory/fast_write_router.py                       71      0     10      0   100%
data/memory/ingestion_hook.py                         279      0     58      0   100%
data/memory/reflective_agent.py                       246      0     50      0   100%
data/memory/shared/shared_memory.py                   115      0     26      0   100%
data/memory/tier3-working/lru_cache.py                132      0     46      0   100%
data/memory/trust.py                                   48      0     12      0   100%
ergebnisse/rekursion/solver/solver.py                   2      0      0      0   100%
ergebnisse/rekursion/solver/solver_improved.py          2      0      0      0   100%
ergebnisse/rekursion/solver/solver_v3.py                4      0      2      0   100%
ergebnisse/rekursion/solver/solver_v3_improved.py       4      0      2      0   100%
ergebnisse/rekursion/solver/solver_v4.py                4      0      2      0   100%
ergebnisse/rekursion/solver/solver_v4_improved.py       4      0      2      0   100%
ergebnisse/rekursion/solver/solver_v5.py                4      0      2      0   100%
ergebnisse/rekursion/solver/solver_v5_improved.py       4      0      2      0   100%
ergebnisse/rekursion/solver/solver_v6.py                4      0      2      0   100%
ergebnisse/rekursion/solver/solver_v6_improved.py       8      0      4      0   100%
skills/procedural_memory.py                            94      0     12      0   100%
-----------------------------------------------------------------------------------------------
TOTAL                                                1651      0    360      0   100%
Required test coverage of 100% reached. Total coverage: 100.00%
============================= 189 passed in 6.50s ==============================
```

### Stand vorher (65 %, nur 4 Module) – zur Einordnung

```text
TOTAL                                263     86    67%
Required test coverage of 65% reached. Total coverage: 67.30%
24 passed in 0.86s
```

Von 4 Modulen/24 Tests (67 %) über 4 Module/35 Tests (100 %) zum **gesamten
Repo-Code**: +10 Module, +95 Tests, +932 Statements.

## 4. Designentscheidungen (jede mit Quelle)

| Entscheidung | Quelle (HTTP 200 am 2026-10-01) |
|---|---|
| `pytest.ini` mit `minversion`, `testpaths`, `addopts`, `markers` | https://docs.pytest.org/en/stable/reference/customize.html |
| `--strict-markers`, Marker-Definition `network` | https://docs.pytest.org/en/stable/example/markers.html |
| LLM-Aufrufe über `monkeypatch` ersetzen (kein Netz) | https://docs.pytest.org/en/stable/how-to/monkeypatch.html |
| Ausgaben der `_demo()`-Funktionen prüfen (`capsys`) | https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html |
| Exit-Code ≠ 0 bei fehlendem/fehlgeschlagenem Test | https://docs.pytest.org/en/stable/reference/exit-codes.html |
| Mindest-Coverage über `--cov-fail-under` (pytest-cov) | https://pytest-cov.readthedocs.io/en/latest/config.html |
| `.coveragerc`: `branch = True`, `exclude_lines` für den `__main__`-Guard | https://coverage.readthedocs.io/en/latest/config.html |
| `--cov-branch` (Line + Branch) | https://pytest-cov.readthedocs.io/en/latest/config.html |
| `# pragma: no branch` für strukturell partielle Zweige | https://coverage.readthedocs.io/en/latest/branch.html |
| `tmp_path`-Fixture für alle Schreibpfade | https://docs.pytest.org/en/stable/how-to/tmp_path.html |
| `Makefile` als dünner Wrapper um den pytest-CLI | https://www.gnu.org/software/make/manual/make.html |
| pytest selbst | https://docs.pytest.org/en/stable/ |

**Nicht verwendet, weil so nicht belegt:** pytest kennt **keinen** eingebauten
„Bestehens-Score" (kein Prozentsatz bestandener Tests als ini-Option). Die
Mindest-Coverage kommt von pytest-cov, einem separaten Plugin – in `pytest.ini`
als solches benannt, nicht als pytest-Kernfunktion.

**Was 100 % hier bedeuten:** **Line + Branch**-Coverage (`branch = True` in
`.coveragerc`, `--cov-branch` in `pytest.ini`; coverage-Doku
https://coverage.readthedocs.io/en/latest/branch.html). Eine strukturell
unerreichbare Verzweigung ist mit der dokumentierten Direktive
`# pragma: no branch` markiert (`lru_cache.py:175`, Begründung:
`ergebnisse/branch-coverage.md` §4). Ausgenommen sind ausschließlich die
`if __name__ == "__main__":`-Blöcke (gemessen: mit Ausnahme 1651 Statements,
mit `--cov-config=/dev/null` 1301 → **106 Statements** in `__main__`-Blöcken,
die ein Import nie erreicht). Die Ausnahme steht sichtbar in `.coveragerc`, es
wird keine weitere Zeile versteckt.

**Fallstrick (dokumentiert):** `asyncio.Queue` bindet an den Loop bei der
Erzeugung. `EnrichmentQueue`/`IngestionHook` müssen daher **innerhalb** der
Coroutine erzeugt werden, sonst: „Future attached to a different loop".

## 5. Netzwerk-Policy (warum `make test` offline läuft)

- `fast_write_router.py` legt beim Import `OpenAI(...)` an und wirft ohne Key
  (`openai.OpenAIError: Missing credentials`). `tests/conftest.py` setzt daher
  **vor** dem Import eine Platzhalter-Key und `OPENAI_BASE_URL=http://127.0.0.1:9`
  – ein versehentlicher Live-Aufruf schlägt sofort fehl; zusätzlich werden
  `FWR_SMALL_MODEL`/`FWR_LARGE_MODEL` entfernt, damit die Code-Defaults
  (AGENTS.md:252) getestet werden.
- Die optionalen LLM-Schritte in `ingestion_hook`/`reflective_agent` werden über
  ein Fake-Modul `openai` in `sys.modules` geprüft (Erfolg, leere Antwort,
  Fehlerfall) – inklusive `reasoning_content`-Fallback.
- Der GLiNER-Pfad läuft gegen ein Fake-Modell; `gliner_available()` wird für
  beide Ausgänge getestet (`sys.modules["gliner"]` gesetzt bzw. `None`).
- Alle Schreibpfade (Ingestion-Log, Tier-2-Index, `knowledge/structured`,
  Skill-Versionen, Audit-Log, Shared-Store) zeigen auf `tmp_path` bzw.
  `/tmp/opencode`; **das Repo bleibt während der Tests unverändert**
  (`git status` nach dem Lauf geprüft).

## 6. Befunde aus dem Testaufbau (ehrlich)

| Befund | Status |
|---|---|
| **`reflective_agent.py:99` IndexError** – liefert das LLM eine Matrix falscher Form (z. B. 2×2 bei k=4), überschrieb `delta` die frische K×K-Matrix und die Heuristik warf `IndexError` | **behoben in Rekursion 032** (`candidate`-Prüfung, strenge K×K-Form): `ergebnisse/rekursion/032-fix-reflective-agent.md` |
| `lru_cache._evict_lru` bei ausschließlich gepinnten Items → `None` (kein Überlauf möglich) | getestet, kein Fehler |
| Solver-Snapshots v1–v6 enthalten absichtliche Fehler (Duplikate, erstes Element, Integer-Division, unsortierter Median) | getestet als Ist-Verhalten + Korrektur der „improved"-Varianten |
| `data/memory/README.md` sagt `versions/v1`,`v2`,`v3`,`v4`; Verzeichnisse vorhanden | getestet |

## 7. Gate-Status / Drift (§9, §9.1c)

- **Produktionscode:** unverändert in diesem Auftrag (nur `tests/**`, `pytest.ini`,
  `.coveragerc`, `Makefile`, `.gitignore`, Doku).
- **Konfigurationsänderungen:** Mindest-Score 65 % → 100 % und Ausweitung des
  Messumfangs auf den gesamten Repo-Code – angeordnet durch den Auftraggeber
  am 2026-10-01 („der ci muss auf 100% geprüft", „für die gesamte
  knowledge-agent gebaut für alles") → damit freigegeben; es ist eine
  CI-Schwelle, kein Produktionsverhalten.
- **Neue Quelle:** NEIN – alle zitierten URLs sind Doku-Prüfnachweise (§6),
  keine Wissensquelle.
- **Drift:** 0 % gegenüber dem Stand vor diesem Auftrag (keine bestehende
  Python-Datei verändert).

## 8. Offene Punkte

1. ~~**IndexError-Bug** in `reflective_agent.py:99`~~ → **behoben in Rekursion 032**
   (`ergebnisse/rekursion/032-fix-reflective-agent.md`); Tests angepasst.
2. ~~**Branch-Coverage ist aus**~~ → **aktiviert 2026-10-01** (`--cov-branch`,
   `branch = True`): 360/360 Branches abgedeckt, siehe `ergebnisse/branch-coverage.md`.
3. Kein GitHub-Actions-/CI-Runner-Workflow (`.github/` existiert nicht) –
   Interface-/CI-Änderung → vorher Human-Gate (§9/§10.4).
4. Kein Lint/Formatter (z. B. ruff/black) – nicht beauftragt.
5. Marker `network` ist deklariert, aber es existiert noch **kein** Live-Test.
6. `make test` läuft nicht automatisch vor Commits (kein pre-commit-Hook).
7. Dateizählungen in `systemtest-gesamt.md` (85/237) sind Standaufnahmen und
   durch die neuen Doku-Dateien veraltet.

## 9. Reproduktion

```bash
python3 -m pip install --user pytest pytest-cov   # einmalig
make test
python3 -m pytest tests/test_reflective.py -v
python3 -m pytest -q --cov-branch -k "not reflective and not ingestion"  # erwartet: rc=1
```
