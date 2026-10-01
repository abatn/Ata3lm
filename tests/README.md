# tests/ – minimales Test-Setup (pytest)

> Stand: 2026-10-01 · Aufruf: `make test` (oder `python3 -m pytest`) ·
> Quelle: Python-Standard **pytest** – https://docs.pytest.org/en/stable/

## Ausführen

```bash
make test                 # Makefile → python3 -m pytest
python3 -m pytest         # dasselbe, ohne make
python3 -m pytest tests/test_fwr.py -v
```

Voraussetzungen (am 2026-10-01 gemessen): `pytest 8.4.2`, `pytest-cov 7.1.0`,
`coverage 7.10.7`, Python 3.9.25. Installation: `python3 -m pip install --user pytest pytest-cov`.

**Mindest-Score:** `pytest.ini` → `--cov-fail-under=100` (Gesamt-Coverage der
vier gemessenen Module; gemessener Wert 2026-10-01: **100,00 %**, 245/245
Statements). Zusätzlich schlägt pytest ohnehin mit Exit-Code ≠ 0 fehl, sobald
**ein** Test fällt (https://docs.pytest.org/en/stable/reference/exit-codes.html).

**Was „100 %" heißt:** Statement-Coverage (`branch = False` in `.coveragerc`),
ausgenommen nur der `__main__`-Guard (erreicht ein Import nie). Branch-Coverage
ist **nicht** aktiv. Details: `ergebnisse/ci-setup.md` §2/§4.

## Dateien

| Datei | Inhalt | Tests |
|---|---|---|
| `conftest.py` | `sys.path` für `data/memory/` (kein Package), Netzwerk-Sperre (Platzhalter-Key + Base-URL `127.0.0.1:9`), `FWR_*_MODEL` entfernt | – |
| `test_fwr.py` | Kaskade + Gate (`AGENTS.md:306-307`, §10.1, §10.4), `_ask` mit Fake-Client, `MemRouter`, `compare_router_10` | 12 |
| `test_governance.py` | Zwei-Personen-Flow (§9.3) + Gesetzestext §9/§9.1 | 10 |
| `test_memory.py` | 3-Tier-Struktur, Versionierung v1–v4, PII/Poisoning/Bias-Guards (§9.2), JSD/Drift (§9.1c) | 13 |
| `../pytest.ini` | Konfiguration + Mindest-Score + Marker | – |
| `../.coveragerc` | Coverage-Konfiguration (Statement-Coverage, `__main__`-Ausnahme) | – |
| `../Makefile` | `make test` → `python3 -m pytest` | – |

Gesamt: **35 Tests, alle grün, ~1 s, ohne Netzwerk.**

## Netzwerk-Policy

Es wird **kein** LLM/Endpoint aufgerufen:

- `fast_write_router.py` legt beim Import den OpenAI-Client an; deshalb setzt
  `conftest.py` eine Platzhalter-Key und eine nicht erreichbare Base-URL.
- Jeder LLM-Aufruf (`_ask`) ist über die pytest-Fixture `monkeypatch` durch
  einen Fake-Client ersetzt
  (https://docs.pytest.org/en/stable/how-to/monkeypatch.html).

Marker `network` ist in `pytest.ini` deklariert (https://docs.pytest.org/en/stable/example/markers.html)
und für künftige Live-Tests reserviert – aktuell existiert kein Live-Test
(`--strict-markers` verhindert unbenannte Marker).

## Was NICHT abgedeckt ist

- Der Live-Endpoint (bewusst, Netzwerk) – `_ask` selbst wird mit Fake-Client
  getestet, `MemRouter`/`compare_router_10`/`_demo()` laufen lokal.
- `ingestion_hook.py` und `reflective_agent.py` werden **nicht** gemessen
  (nicht in `--cov`); sie enthalten Netzwerk-/Repo-Schreibpfade.
- Kein Lint/Formatter, kein GitHub-Actions-Workflow (Interface/CI-Änderung →
  Human-Gate nach `AGENTS.md` §9).
