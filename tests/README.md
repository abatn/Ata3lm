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
Gemessen 2026-10-02: **100,00 %** – 1753/1753 Statements **und 396/396 Branches**
über **den gesamten Repo-Code** (`data/memory/**`, `skills/**`,
`ergebnisse/rekursion/solver/**`).

**Was „100 %" heißt:** **Line + Branch**-Coverage (`branch = True` in
`.coveragerc`, `--cov-branch` in `pytest.ini`). Ausgenommen sind nur die
`__main__`-Blöcke (erreicht ein Import nie) und **eine** strukturell
unerreichbare Verzweigung, markiert mit der coverage-Direktive
`# pragma: no branch` (`lru_cache.py:175`; Begründung:
`ergebnisse/branch-coverage.md` §4). Details: `ergebnisse/ci-setup.md` §2/§4.

## Dateien

| Datei | Inhalt | Tests |
|---|---|---|
| `conftest.py` | `sys.path` für `data/memory`, `shared/`, `tier3-working/`, `skills`; Netzwerk-Sperre (Platzhalter-Key + Base-URL `127.0.0.1:9`), `FWR_*_MODEL` entfernt | – |
| `test_fwr.py` | FWR-Kaskade + Gate, `_ask` (Fake-Client), `MemRouter`, `compare_router_10` | 12 |
| `test_governance.py` | Zwei-Personen-Flow (§9.3) inkl. Diff-Bindung + Gesetzestext §9/§9.1 | 13 |
| `test_memory.py` | 3 Tiers, v1–v4, PII/Poisoning/Bias-Guards, JSD/Drift | 14 |
| `test_bi_temporal.py` | valid time × transaction time, Supersede statt Löschen | 5 |
| `test_shared_memory.py` | ACL, Trust-Konflikt (superseded/contested), Schema, Sync, Dump | 8 |
| `test_lru_cache.py` | LRU-/Value-Eviction, Adaptive Forgetting, Tier-2-Auslagerung | 10 |
| `test_ingestion.py` | Privacy/Secret-Filter, Encoding-Gate, GLiNER-Pfade, Graph-Konflikte, Konsolidierung, async Enrichment, Lifecycle | 17 |
| `test_reflective.py` | HMM-Trägheit (SEAA) inkl. NOOP, Hub/Forgetting, Destillation, Dual-Path-Retrieval, Lyapunov | 20 |
| `test_procedural_memory.py` | Skill-Snapshots, Human-Gate-Update, Rollback (alles in `tmp_path`) | 7 |
| `test_evaluator_version.py` | Red-Queen: ε-Best-Belief-Gate, HF-Anker, Selective Erasure, Loop, LLM-Grader (json-repair/Retry/Schema), Statistik, Bootstrap-KI, κ-Statistik | 56 |
| `test_solvers.py` | 9 historische Solver-Snapshots (Ist-Verhalten inkl. bekannter Schwächen) | 20 |
| `test_mandate.py` | Mandat: attenuate-nie-expand, ALLOW/REVIEW/DENY, Grant, Evidence | 9 |
| `test_agents_law.py` | AGENTS.md-Konformität (§1–§11, Guardrails, Provenienz, Versionierung, CI-Verdrahtung) | 8 |
| `../pytest.ini` | Konfiguration + Mindest-Score + Marker | – |
| `../.coveragerc` | Coverage-Konfiguration (Statement-Coverage, `__main__`-Ausnahme) | – |
| `../Makefile` | `make test` → `python3 -m pytest` | – |

Gesamt: **201 Tests, alle grün, ~6,7 s, ohne Netzwerk.**

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

## Befunde

- **`reflective_agent.py:99` (behoben in Rekursion 032):** lieferte das LLM eine
  Matrix falscher Form (z. B. 2×2 bei k=4), überschrieb `delta` die frische
  K×K-Matrix und die Heuristik warf `IndexError`. Fix: die LLM-Matrix wird erst
  als `candidate` geprüft und nur bei K×K übernommen, sonst verworfen.
  Tests: `test_parse_transition_delta_falsche_form_wird_verworfen` +
  `test_parse_transition_delta_4x4_wird_uebernommen`; Beleg:
  `ergebnisse/rekursion/032-fix-reflective-agent.md`.

## Branch-Abdeckung (neu 2026-10-01)

`--cov-branch` + `branch = True`: 396/396 Branches abgedeckt. Fünf partielle
Zweige gab es anfangs – vier wurden mit echten Pfaden getestet, einer ist
strukturell unerreichbar:

| Datei:Zeile | Bogen | Abdeckung |
|---|---|---|
| `bias_monitor.py:61` | `61->74` (Schleife läuft 0×) | `test_capped_simplex_ohne_iterationen` (`iters=0`) |
| `ingestion_hook.py:246` | `246->244` (Entity schon im Graph) | `test_update_graph_knoten_bereits_vorhanden` |
| `shared_memory.py:142` | `142->140` (Key ohne Konflikt) | `test_sync_ohne_konflikt_bei_gleichem_wert` |
| `lru_cache.py:152` | `152->144` (Item sofort verdrängt) | `test_fill_from_structured_ohne_aufnahme_bei_vollem_cache` |
| `lru_cache.py:175` | `175->167` (`freq*crit >= 0.8` immer wahr) | `# pragma: no branch` (unerreichbar, begründet) |

Volle Analyse: `ergebnisse/branch-coverage.md`.

## Was NICHT abgedeckt ist

- Der Live-Endpoint (bewusst, Netzwerk).
- Nicht-Python-Dateien (Markdown/Docs/JSON) – Coverage misst Code.
- Kein Lint/Formatter, kein GitHub-Actions-Workflow (Interface/CI-Änderung →
  Human-Gate nach `AGENTS.md` §9).
