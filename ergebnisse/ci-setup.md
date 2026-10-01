# CI-Setup: pytest für den Knowledge-Agenten

> Datum: 2026-10-01 · Auftrag: minimales CI/pytest-Setup, „Quelle = Python-Standard
> (pytest)" · Lab-Prinzip §6: nur Behauptungen, die in der pytest-Doku stehen
> (URL-Tabelle unten, HTTP 200 am 2026-10-01 geprüft) bzw. lokal nachlauffähig sind.

## 1. Gelieferte Dateien (neu, kein bestehendes Modul verändert)

| Datei | Zweck |
|---|---|
| `tests/conftest.py` | `sys.path` (data/memory ist kein Package) + Netzwerk-Sperre |
| `tests/test_fwr.py` | 12 Tests: Kaskade + Gate (`AGENTS.md:306-307`, §10.1, §10.4), `_ask` (Fake-Client), MemRouter, `compare_router_10` |
| `tests/test_governance.py` | 10 Tests: Zwei-Personen-Flow (§9.3) + Gesetzestext §9/§9.1 |
| `tests/test_memory.py` | 13 Tests: 3 Tiers, v1–v4, PII/Poisoning/Bias-Guards, JSD/Drift, `_demo`s |
| `pytest.ini` | Konfiguration + **Mindest-Score** (`--cov-fail-under=100`) + Marker |
| `.coveragerc` | Coverage-Konfiguration; nimmt **nur** den `__main__`-Guard aus |
| `Makefile` | `make test` → `python3 -m pytest` (+ `make clean`) |
| `tests/README.md` | Bedienung, Netzwerk-Policy, Abdeckung |
| `.gitignore` | +4 Zeilen: `.pytest_cache/`, `.coverage`, `coverage.xml`, `htmlcov/` |
| `ergebnisse/systemtest-gesamt.md` | offener Punkt 6 („Kein CI/pytest") als erledigt markiert |

## 2. Zwei Scores – nicht verwechseln

| Score | Definition | Quelle | Umsetzung |
|---|---|---|---|
| **§9-Test-Score** | bestandene Tests / Gesamttests (≥95 allow, 70–94 ask, <70 deny) | `AGENTS.md` §9 | pytest Exit-Code ≠ 0 bei **jedem** fehlgeschlagenen Test → `make test` schlägt fehl; ein „Score von 100 %" ist die einzige grüne Variante |
| **Mindest-Score (Coverage)** | abgedeckte Statements / alle Statements der 4 gemessenen Module | pytest-cov `--cov-fail-under` (pytest-cov-Doku) | `pytest.ini`: **100 %** (gemessen: 100,00 %, 245/245 Statements) |

Beide Gates sind **gemessen** (Rohtexte unten): ein fehlgeschlagenes Test
liefert `rc=1`; ein unterschrittener Coverage-Wert liefert `rc=1` trotz
„33 passed".

**100 ist das Maximum:** `--cov-fail-under=101` wird von pytest-cov abgelehnt
(`error: argument --cov-fail-under: … The maximum value is 100.`, `rc=4`).
Nachweis der 100-%-Schwelle daher über *weniger* Tests:
`pytest -k "not memrouter and not compare_router"` → **91,43 % → FAIL, `rc=1`**.

## 3. Rohtext `make test` (2026-10-01, 100 %)

```text
python3 -m pytest
============================= test session starts ==============================
platform linux -- Python 3.9.25, pytest-8.4.2, pluggy-1.6.0
rootdir: /home/opc/knowledge-agent
configfile: pytest.ini
testpaths: tests
plugins: cov-7.1.0, asyncio-1.2.0, langsmith-0.4.37, anyio-4.12.1
collected 35 items

tests/test_fwr.py ............                                           [ 34%]
tests/test_governance.py ..........                                      [ 62%]
tests/test_memory.py .............                                       [100%]

================================ tests coverage ================================
Name                               Stmts   Miss  Cover   Missing
----------------------------------------------------------------
data/memory/approval.py               42      0   100%
data/memory/bias_monitor.py           84      0   100%
data/memory/fast_write_router.py      71      0   100%
data/memory/trust.py                  48      0   100%
----------------------------------------------------------------
TOTAL                                245      0   100%
Required test coverage of 100% reached. Total coverage: 100.00%
============================== 35 passed in 0.94s ==============================
```

### Stand vor der 100-%-Anhebung (65 %, nur zur Einordnung)

```text
TOTAL                                263     86    67%
Required test coverage of 65% reached. Total coverage: 67.30%
24 passed in 0.86s
data/memory/fast_write_router.py      83     43    48%   37-45, 120-121, 125-134, 139-144, 149-171, 181-199
```

Damit ist nachvollziehbar, welche Tests die 100 % erbracht haben: `_ask`
(Fake-Client statt Netz), `MemRouter`/`compare_router_10`, `_embed_router`,
die drei `_demo()`-Funktionen und die `bereits approved`-Verzweigung.


**Warum FWR nur 48 %:** nicht getestet sind `_ask` (37–45, Netzwerk),
`MemRouter` (120–171) und `_demo` (181–199) – bewusst, weil sie Live-Aufrufe
bzw. Ausgaben sind.

### Gates nachgewiesen (Rohtexte)

```text
--- Nachweis der 100-%-Schwelle: zwei Tests weggelassen ---
$ python3 -m pytest -q -k "not memrouter and not compare_router"
TOTAL                                245     21    91%
FAIL Required test coverage of 100% not reached. Total coverage: 91.43%
33 passed, 2 deselected in 0.91s
rc=1 (erwartet 1)

--- 101 % ist nicht konfigurierbar (Maximum der Schwelle) ---
$ python3 -m pytest -q --cov-fail-under=101
error: argument --cov-fail-under: Your desire for over-achievement is admirable
but misplaced. The maximum value is 100. Perhaps write more integration tests?
rc=4 (erwartet 4)

--- absichtlich fehlgeschlagener Test ---
rc=1 (erwartet 1)
```

## 4. Designentscheidungen (jede mit Quelle)

| Entscheidung | Quelle (HTTP 200 am 2026-10-01) |
|---|---|
| `pytest.ini` mit `minversion`, `testpaths`, `addopts`, `markers` | https://docs.pytest.org/en/stable/reference/customize.html |
| `--strict-markers`, Marker-Definition `network` | https://docs.pytest.org/en/stable/example/markers.html |
| LLM-Aufrufe über `monkeypatch` skripten (kein Netz) | https://docs.pytest.org/en/stable/how-to/monkeypatch.html |
| Ausgaben der `_demo()`-Funktionen prüfen (`capsys`) | https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html |
| Exit-Code ≠ 0 bei fehlendem/fehlgeschlagenem Test | https://docs.pytest.org/en/stable/reference/exit-codes.html |
| Mindest-Coverage über `--cov-fail-under` (pytest-cov) | https://pytest-cov.readthedocs.io/en/latest/config.html |
| `.coveragerc`: `branch = False`, `exclude_lines` für den `__main__`-Guard | https://coverage.readthedocs.io/en/latest/config.html |
| `Makefile` als dünner Wrapper um den pytest-CLI | https://www.gnu.org/software/make/manual/make.html |
| pytest selbst | https://docs.pytest.org/en/stable/ |

**Nicht verwendet, weil es so nicht belegt ist:** pytest kennt **keinen**
eingebauten „Bestehens-Score" (kein Prozentsatz bestandener Tests als
ini-Option). Die Mindest-Coverage kommt deshalb von pytest-cov, einem separaten
Plugin – das ist in `pytest.ini` als solches benannt, nicht als pytest-Kernfunktion.

**Was 100 % hier bedeuten:** Statement-Coverage der vier Module
(`branch = False`, in `.coveragerc` ausdrücklich gesetzt) – **kein**
Branch-Coverage. Ausgenommen ist ausschließlich der `__main__`-Guard
(4 Zeilen), weil ein Import ihn nie erreicht; die Ausnahme steht sichtbar in
`.coveragerc`, es wird keine weitere Zeile versteckt.

## 5. Netzwerk-Policy (warum `make test` offline läuft)

`fast_write_router.py` legt beim Import `OpenAI(...)` an und wirft ohne Key
(`openai.OpenAIError: Missing credentials`). `tests/conftest.py` setzt daher
**vor** dem Import eine Platzhalter-Key und `OPENAI_BASE_URL=http://127.0.0.1:9`
– ein versehentlicher Live-Aufruf schlägt sofort fehl, statt das Endpoint zu
treffen; zusätzlich werden `FWR_SMALL_MODEL`/`FWR_LARGE_MODEL` entfernt, damit
die Code-Defaults (AGENTS.md:252) getestet werden. Alle Modell-Antworten sind
skriptet.

## 6. Gate-Status / Drift (§9, §9.1c)

- **Verhaltensänderung:** NEIN – es wurden keine Produktionsfunktionen geändert;
  `.gitignore` +4 Zeilen (Artefakte), `.coveragerc` (neu) und ein
  Textzeilen-Nachtrag in `systemtest-gesamt.md` sind keine Interface-Änderung.
- **Konfigurationsänderung (Mindest-Score 65 % → 100 %):** angeordnet durch den
  Auftraggeber am 2026-10-01 („der ci muss auf 100% geprüft") → damit
  freigegeben; die Anhebung ist eine CI-Schwelle, kein Produktionsverhalten.
- **Neue Quelle:** NEIN – es kam kein Paper/URL-Neuzugang hinzu; alle
  zitierten Doku-URLs sind Prüfnachweise (§6), keine Wissensquelle.
- **Drift:** keine bestehende Python-Datei verändert (nur neue Dateien) →
  Drift = 0 % gegenüber dem Stand vor diesem Auftrag.
- **Abhängigkeit zum FWR-Gate:** `tests/test_fwr.py` prüft die **neue**
  `classify()`-Logik (Write-Fix). Das Gate wurde am 2026-10-01 freigegeben
  (§9 Human-Gate `approved`, `ergebnisse/fwr-code-korrektur.md` §0) – die drei
  betroffenen Assertions (`write-update`, `write-new`, `uncertain`) sichern
  dauerhaft, dass die Bedingungen `AGENTS.md:306-307` erfüllt bleiben.

## 7. Offene Punkte

1. Kein GitHub-Actions-/CI-Runner-Workflow (`.github/` existiert nicht) –
   Interface-/CI-Änderung → vorher Human-Gate (§9/§10.4).
2. Kein Lint/Formatter (z. B. ruff/black) – nicht beauftragt.
3. **Branch-Coverage ist aus** (`branch = False` in `.coveragerc`): 100 %
   bedeutet 100 % der Statements, nicht aller Verzweigungen.
4. Marker `network` ist deklariert, aber es existiert noch **kein** Live-Test
   (kostenpflichtige/latenzabhängige LLM-Läufe).
5. `make test` läuft nicht automatisch vor Commits (kein pre-commit-Hook).
6. Ergebnis-Zeilen der Dateizählung in `systemtest-gesamt.md` (Zeile 21: 85,
   Zeile 26: 237) sind Standaufnahmen vom 2026-10-01 und durch `ci-setup.md` +
   `fwr-code-korrektur.md` inzwischen veraltet. Nachmessung 2026-10-01 mit
   anderem Zählpfad (Zwecke klar benennen, wenn neu gezählt wird):
   `find ergebnisse -name '*.md' | wc -l` → **136**, inklusive `rekursion/`;
   `ls ergebnisse/*.md | wc -l` → **79**; gesamt
   `find . -name '*.md' -not -path './.git/*' | wc -l` → **241**.

## 8. Reproduktion

```bash
python3 -m pip install --user pytest pytest-cov   # einmalig
make test
python3 -m pytest tests/test_fwr.py -v
python3 -m pytest -q -k "not memrouter and not compare_router"   # erwartet: rc=1 (91 %)
```
