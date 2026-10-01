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

**Mindest-Score:** `pytest.ini` → `--cov-fail-under=65` (Gesamt-Coverage der
vier gemessenen Module; gemessener Wert 2026-10-01: **67,30 %**).
Zusätzlich schlägt pytest ohnehin mit Exit-Code ≠ 0 fehl, sobald **ein** Test
fällt (https://docs.pytest.org/en/stable/reference/exit-codes.html).

## Dateien

| Datei | Inhalt | Tests |
|---|---|---|
| `conftest.py` | `sys.path` für `data/memory/` (kein Package), Netzwerk-Sperre (Platzhalter-Key + Base-URL `127.0.0.1:9`), `FWR_*_MODEL` entfernt | – |
| `test_fwr.py` | 3-Klassen-Kaskade + Gate (`AGENTS.md:306-307`, §10.1, §10.4) | 7 |
| `test_governance.py` | Zwei-Personen-Flow (§9.3) + Gesetzestext §9/§9.1 | 8 |
| `test_memory.py` | 3-Tier-Struktur, Versionierung v1–v4, PII/Poisoning/Bias-Guards (§9.2), Drift (§9.1c) | 9 |
| `../pytest.ini` | Konfiguration + Mindest-Score + Marker | – |
| `../Makefile` | `make test` → `python3 -m pytest` | – |

Gesamt: **24 Tests, alle grün, 0,9 s, ohne Netzwerk.**

## Netzwerk-Policy

Es wird **kein** LLM/Endpoint aufgerufen:

- `fast_write_router.py` legt beim Import den OpenAI-Client an; deshalb setzt
  `conftest.py` eine Platzhalter-Key und eine nicht erreichbare Base-URL.
- Jeder LLM-Aufruf (`_ask`) ist in `test_fwr.py` über die pytest-Fixture
  `monkeypatch` skriptet
  (https://docs.pytest.org/en/stable/how-to/monkeypatch.html).

Marker `network` ist in `pytest.ini` deklariert (https://docs.pytest.org/en/stable/example/markers.html)
und für künftige Live-Tests reserviert – aktuell existiert kein Live-Test
(`--strict-markers` verhindert unbenannte Marker).

## Was NICHT abgedeckt ist

- `_ask` / Live-Endpoint (bewusst, Netzwerk), `_demo`-Funktionen, `MemRouter`,
  `ingestion_hook`, `reflective_agent` → daher die Gesamt-Coverage von 67 %.
- Kein Lint/Formatter, kein GitHub-Actions-Workflow (Interface/CI-Änderung →
  Human-Gate nach `AGENTS.md` §9).
