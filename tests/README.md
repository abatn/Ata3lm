# tests/ – pytest-Setup für den gesamten Knowledge-Agenten

> Stand: 2026-10-01 · Aufruf: `make test` (oder `python3 -m pytest`) ·
> Quelle: Python-Standard **pytest** – https://docs.pytest.org/en/stable/

## Ausführen

```bash
make test                 # Makefile → python3 -m pytest
python3 -m pytest         # dasselbe, ohne make
python3 -m pytest tests/test_reflective.py -v
```

Voraussetzungen (am 2026-10-01 gemessen): `pytest 8.4.2`, `pytest-cov 7.1.0`,
`coverage 7.10.7`, `numpy 2.0.2`, Python 3.9.25.
Installation: `python3 -m pip install --user pytest pytest-cov`.

**Mindest-Score:** `pytest.ini` → `--cov-fail-under=100`.
Gemessen 2026-10-01: **100,00 %** – 1198/1198 Statements über **den gesamten
Repo-Code** (`data/memory/**`, `skills/**`, `ergebnisse/rekursion/solver/**`).

**Was „100 %" heißt:** Statement-Coverage (`branch = False` in `.coveragerc`),
ausgenommen nur der `__main__`-Guard (erreicht ein Import nie). Branch-Coverage
ist **nicht** aktiv. Details: `ergebnisse/ci-setup.md` §2/§4.

## Dateien

| Datei | Inhalt | Tests |
|---|---|---|
| `conftest.py` | `sys.path` für `data/memory`, `shared/`, `tier3-working/`, `skills`; Netzwerk-Sperre (Platzhalter-Key + Base-URL `127.0.0.1:9`), `FWR_*_MODEL` entfernt | – |
| `test_fwr.py` | FWR-Kaskade + Gate, `_ask` (Fake-Client), `MemRouter`, `compare_router_10` | 12 |
| `test_governance.py` | Zwei-Personen-Flow (§9.3) + Gesetzestext §9/§9.1 | 10 |
| `test_memory.py` | 3 Tiers, v1–v4, PII/Poisoning/Bias-Guards, JSD/Drift | 13 |
| `test_bi_temporal.py` | valid time × transaction time, Supersede statt Löschen | 5 |
| `test_shared_memory.py` | ACL, Trust-Konflikt (superseded/contested), Schema, Sync, Dump | 7 |
| `test_lru_cache.py` | LRU-/Value-Eviction, Adaptive Forgetting, Tier-2-Auslagerung | 9 |
| `test_ingestion.py` | Privacy/Secret-Filter, Encoding-Gate, GLiNER-Pfade, Graph-Konflikte, Konsolidierung, async Enrichment, Lifecycle | 16 |
| `test_reflective.py` | HMM-Trägheit (SEAA), Hub/Forgetting, Destillation, Dual-Path-Retrieval, Lyapunov | 15 |
| `test_procedural_memory.py` | Skill-Snapshots, Human-Gate-Update, Rollback (alles in `tmp_path`) | 7 |
| `test_solvers.py` | 9 historische Solver-Snapshots (Ist-Verhalten inkl. bekannter Schwächen) | 20 |
| `../pytest.ini` | Konfiguration + Mindest-Score + Marker | – |
| `../.coveragerc` | Coverage-Konfiguration (Statement-Coverage, `__main__`-Ausnahme) | – |
| `../Makefile` | `make test` → `python3 -m pytest` | – |

Gesamt: **114 Tests, alle grün, ~1,6 s, ohne Netzwerk.**

## Netzwerk-Policy

Es wird **kein** LLM/Endpoint aufgerufen:

- `fast_write_router.py` legt beim Import den OpenAI-Client an; deshalb setzt
  `conftest.py` eine Platzhalter-Key und eine nicht erreichbare Base-URL.
- LLM-Aufrufe werden ersetzt: `_ask` per Fake-Client (`test_fwr.py`), die
  optionalen LLM-Schritte in `ingestion_hook`/`reflective_agent` per Fake-Modul
  `openai` in `sys.modules` (`monkeypatch`).
- Der GLiNER-Pfad wird mit einem Fake-Modell geprüft; `gliner_available()`
  wird für beide Ausgänge getestet.
- Schreibpfade (Logs, Tier 2, `knowledge/structured`, Skill-Versionen) zeigen
  in `tmp_path` – das Repo bleibt während der Tests unverändert.

Marker `network` ist in `pytest.ini` deklariert und für künftige Live-Tests
reserviert; aktuell existiert kein Live-Test (`--strict-markers` verhindert
unbenannte Marker).

## Befunde (dokumentiert, nicht behoben)

- **`reflective_agent.py:99` (IndexError):** liefert das LLM eine Matrix
  falscher Form (z. B. 2×2 bei k=4), läuft die Heuristik auf dem falschen Array
  weiter und wirft `IndexError`. Test:
  `test_reflective.py::test_parse_transition_delta_falsche_form_crasht`.
  Ein Fix wäre eine Verhaltensänderung → Human-Gate (§9).

## Was NICHT abgedeckt ist

- Der Live-Endpoint (bewusst, Netzwerk).
- Nicht-Python-Dateien (Markdown/Docs/JSON) – Coverage misst Code.
- Kein Lint/Formatter, kein GitHub-Actions-Workflow (Interface/CI-Änderung →
  Human-Gate nach `AGENTS.md` §9).
